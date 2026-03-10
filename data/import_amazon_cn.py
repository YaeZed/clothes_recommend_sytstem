"""
import_amazon_cn.py
───────────────────────────────────────────────────────────────────────
从 Amazon Fashion metadata 导入真实服装数据（图片 + 商品名翻译为中文）

步骤：
  1. 解析 meta_Clothing_Shoes_and_Jewelry.json.gz
  2. 只保留【有真实服装图片 & 有商品标题 & 分类不含 Watch/Handbag 等杂类】的条目
  3. 用 deep-translator 把英文标题翻译成中文（批量，带速率限制）
  4. 清空 products & user_behaviors & recommendations 表，重新写入
  5. 重新生成行为数据（购买/浏览记录）

运行方法：
    python data/import_amazon_cn.py
"""

import gzip, ast, json, sys, os, time, random, string
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from deep_translator import GoogleTranslator
from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product
from backend.models.user import User
from backend.models.behavior import UserBehavior, Recommendation
from werkzeug.security import generate_password_hash

# ── 配置 ────────────────────────────────────────────────────────────
RAW_DIR   = os.path.join(os.path.dirname(__file__), "raw")
META_FILE = os.path.join(RAW_DIR, "meta_Clothing_Shoes_and_Jewelry.json.gz")

MAX_PRODUCTS = 500    # 导入商品数（500条足够演示）
MAX_BEHAVIORS = 20000 # 生成行为数

# 过滤掉非服装类别的关键词（Amazon数据包含手表、包袋等）
EXCLUDE_KEYWORDS = [
    "watch", "clock", "jewelry", "necklace", "bracelet", "ring",
    "earring", "pendant", "handbag", "wallet", "purse", "luggage",
    "bag", "backpack", "tote", "duffel", "suitcase", "briefcase",
    "pouch", "satchel", "drawstring", "waist", "crossbody"
]

# 类目映射 + 中文描述
CATEGORY_MAP = {
    "shirt":   "上衣",  "blouse": "上衣", "top": "上衣",
    "tee":     "上衣",  "polo":   "上衣",
    "pants":   "裤子",  "jeans":  "裤子", "legging": "裤子", "trouser": "裤子",
    "dress":   "裙子",  "skirt":  "裙子", "gown": "裙子",
    "coat":    "外套",  "jacket": "外套", "blazer": "外套", "sweater": "外套",
    "hoodie":  "卫衣",  "sweatshirt": "卫衣", "pullover": "卫衣",
    "shoe":    "鞋子",  "sneaker": "鞋子", "boot": "鞋子", "sandal": "鞋子",
    "scarf":   "配饰",  "hat": "配饰", "glove": "配饰", "belt": "配饰",
}

STYLE_LIST   = ["休闲", "正式", "运动", "街头", "复古", "简约", "时尚", "森系", "潮流"]
MATERIAL_MAP = {
    "上衣": ["纯棉", "棉质混纺", "雪纺", "针织"],
    "裤子": ["牛仔布", "棉麻", "聚酯纤维", "弹力布"],
    "裙子": ["雪纺", "真丝感", "棉质", "蕾丝"],
    "外套": ["羊毛混纺", "棉质", "涤纶", "针织"],
    "卫衣": ["全棉", "绒布", "抓绒", "混棉"],
    "鞋子": ["帆布", "真皮", "人造革", "网布"],
    "配饰": ["针织", "真皮", "合金", "棉麻"],
}

DESC_TEMPLATES = [
    "{mat}面料精心制作，质感细腻，穿着轻盈舒适。{style}风格设计，简约而不失时尚感，适合多种场合穿着搭配。",
    "精选优质{mat}，版型经典百搭。{style}风格，上身效果极佳，展现个人品味，春夏秋冬皆宜。",
    "采用{mat}材质，亲肤透气，深受时尚达人喜爱。{style}设计理念，轻松打造精致潮流造型。",
    "优质{mat}面料，经典{style}风格款式，多色可选，搭配灵活百变，日常通勤、周末休闲均适宜。",
]

TAGS_MAP = {
    "上衣": ["百搭", "宽松", "显瘦", "纯色"],
    "裤子": ["修身", "显瘦", "高腰", "休闲"],
    "裙子": ["显瘦", "仙气", "优雅", "甜美"],
    "外套": ["保暖", "百搭", "时尚", "显瘦"],
    "卫衣": ["宽松", "保暖", "休闲", "潮流"],
    "鞋子": ["舒适", "透气", "时尚", "百搭"],
    "配饰": ["精致", "时尚", "百搭", "小众"],
}


def parse_gz(filepath):
    with gzip.open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                try:
                    yield ast.literal_eval(line)
                except Exception:
                    continue


def detect_category(title: str, cats: list) -> str:
    text = (title + " " + " ".join(cats)).lower()
    for kw, cat in CATEGORY_MAP.items():
        if kw in text:
            return cat
    return None  # 返回 None 表示无法识别，后续过滤


def is_excluded(title: str, cats: list) -> bool:
    text = (title + " " + " ".join(cats)).lower()
    return any(kw in text for kw in EXCLUDE_KEYWORDS)


def translate_batch(texts: list, batch_size=20, delay=1.5) -> list:
    """分批翻译，避免触发速率限制"""
    translator = GoogleTranslator(source="en", target="zh-CN")
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            try:
                zh = translator.translate(text[:200])  # 限制长度
                results.append(zh or text)
            except Exception:
                results.append(text)  # 翻译失败保留英文
        print(f"  翻译进度: {min(i + batch_size, len(texts))} / {len(texts)}")
        time.sleep(delay)  # 友好速率限制
    return results


def gen_desc(category, style):
    mat  = random.choice(MATERIAL_MAP.get(category, ["棉质"]))
    tpl  = random.choice(DESC_TEMPLATES)
    return tpl.format(mat=mat, style=style)


def collect_items(max_count):
    """解析 metadata，筛选出合适的服装条目"""
    print(f"\n[1/4] 从 Amazon metadata 筛选服装条目（最多 {max_count} 件）...")
    items = []
    for raw in parse_gz(META_FILE):
        if len(items) >= max_count:
            break
        title = (raw.get("title") or "").strip()
        cats  = []
        raw_cats = raw.get("categories") or []
        if raw_cats and isinstance(raw_cats[0], list):
            cats = raw_cats[0]
        elif isinstance(raw_cats, list):
            cats = raw_cats

        img = raw.get("imUrl") or ""
        if not img or not img.startswith("http") or not title:
            continue
        if "images-amazon.com" not in img and "ssl-images-amazon" not in img:
            continue
        if is_excluded(title, cats):
            continue
        cat = detect_category(title, cats)
        if not cat:
            continue

        price_raw = raw.get("price") or "0"
        try:
            price = float(str(price_raw).replace("$", "").replace(",", "").strip() or 0)
            if price > 1000 or price < 0:
                price = round(random.uniform(50, 600), 2)
        except ValueError:
            price = round(random.uniform(50, 600), 2)

        items.append({
            "en_title": title,
            "category": cat,
            "price":    price,
            "image":    img,
            "desc_en":  (raw.get("description") or "")[:300],
        })

    print(f"  筛选到 {len(items)} 件合适的服装商品")
    return items


def translate_titles(items):
    print(f"\n[2/4] 翻译商品标题（{len(items)} 条，约需 {len(items)//20 * 2} 秒）...")
    titles_en = [it["en_title"] for it in items]
    titles_zh = translate_batch(titles_en, batch_size=20, delay=1.5)
    for it, zh in zip(items, titles_zh):
        it["zh_title"] = zh
    return items


def load_into_db(app, items):
    print(f"\n[3/4] 写入 MySQL（清空旧数据后重新导入）...")
    with app.app_context():
        # 清空顺序：有外键依赖的先删
        db.session.execute(db.text("DELETE FROM recommendations"))
        db.session.execute(db.text("DELETE FROM user_behaviors"))
        db.session.execute(db.text("DELETE FROM products WHERE 1=1"))
        db.session.commit()
        print("  旧数据已清空")

        for i, it in enumerate(items):
            style    = random.choice(STYLE_LIST)
            category = it["category"]
            tag_pool = TAGS_MAP.get(category, ["时尚", "百搭"])

            p = Product(
                title       = it["zh_title"][:200],
                category    = category,
                style       = style,
                price       = it["price"] if it["price"] > 0 else round(random.uniform(50, 600), 2),
                sales_count = random.randint(20, 8000),
                stock       = random.randint(10, 300),
                images      = [it["image"]],
                description = gen_desc(category, style),
                tags        = random.sample(tag_pool, min(3, len(tag_pool))),
                attributes  = {
                    "color": random.sample(["黑色", "白色", "红色", "蓝色", "绿色", "灰色", "粉色", "米色"], 3),
                    "size":  ["S", "M", "L", "XL"],
                },
            )
            db.session.add(p)
            if i % 100 == 0:
                db.session.flush()
                print(f"  写入商品: {i} / {len(items)}")

        db.session.commit()
        print(f"  ✅ 商品写入完成，共 {len(items)} 条")


def gen_behaviors(app):
    print(f"\n[4/4] 重新生成用户行为数据（{MAX_BEHAVIORS} 条）...")
    with app.app_context():
        products = Product.query.all()
        users    = User.query.filter_by(role="user").all()

        if not users:
            # 自动创建测试用户
            print("  没有普通用户，自动创建 100 个测试用户...")
            users = []
            for i in range(1, 101):
                u = User(
                    username  = f"user{i:03d}",
                    password  = generate_password_hash("123456"),
                    style_pref = random.sample(STYLE_LIST, 2),
                    size_info  = {"height": random.randint(155, 185), "weight": random.randint(45, 90)},
                )
                db.session.add(u)
                users.append(u)
            db.session.flush()

        action_weights = ["view"] * 5 + ["collect"] * 2 + ["cart"] * 2 + ["purchase"]
        count = 0
        for _ in range(MAX_BEHAVIORS):
            p = random.choice(products)
            u = random.choice(users)
            behavior = UserBehavior(
                user_id     = u.id,
                product_id  = p.id,
                action_type = random.choice(action_weights),
                duration    = random.randint(5, 300),
            )
            db.session.add(behavior)
            count += 1
            if count % 2000 == 0:
                db.session.flush()
                print(f"  行为数据: {count} / {MAX_BEHAVIORS}")

        db.session.commit()
        print(f"  ✅ 行为数据生成完成，{count} 条")


if __name__ == "__main__":
    if not os.path.exists(META_FILE):
        print(f"❌ 找不到 Amazon metadata 文件：{META_FILE}")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        db.create_all()

    items = collect_items(MAX_PRODUCTS)
    if not items:
        print("❌ 未能提取到任何服装条目，请检查数据文件格式")
        sys.exit(1)

    items = translate_titles(items)
    load_into_db(app, items)
    gen_behaviors(app)

    print("\n🎉 Amazon 中文化服装数据导入完毕！")
    print("下一步：重新运行推荐算法 notebooks，或直接访问前端查看效果")
