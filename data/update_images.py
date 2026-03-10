"""
update_images.py
从已下载的 Amazon Fashion metadata 文件提取真实服装图片URL，
批量更新 MySQL products 表里的 images 字段。

同时用更真实的中文商品描述替换原来的占位文字。

运行方法：
    python data/update_images.py
"""
import gzip, ast, json, sys, os, random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product

RAW_DIR   = os.path.join(os.path.dirname(__file__), "raw")
META_FILE = os.path.join(RAW_DIR, "meta_Clothing_Shoes_and_Jewelry.json.gz")

# ── 真实中文商品描述模板 ─────────────────────────────────────────
DESC_TEMPLATES = {
    "上衣": [
        "采用{material}面料，亲肤透气，{fit}版型设计，适合{season}穿着。领口{neck}，搭配{style}风格裤装效果极佳。",
        "精选{material}材质，手感柔软舒适。{style}风格设计，{fit}版型，轻松打造时尚休闲造型。",
        "{material}面料，吸湿排汗，{fit}设计适合多种身材。色调百搭，是{season}必备单品。",
    ],
    "裤子": [
        "高腰{style}版型，修饰腿部线条。{material}面料，穿着舒适，{season}必备百搭单品。",
        "经典{style}款式，{material}制成，弹性好易打理。搭配任何上衣都能轻松驾驭。",
        "{fit}裁剪，展现优雅身姿。{material}材质，不易变形，日常通勤、休闲出游均适宜。",
    ],
    "裙子": [
        "浪漫{style}设计，{material}质地飘逸轻盈。腰部{fit}剪裁，展现完美曲线，{season}出行首选。",
        "时尚{style}风格，采用优质{material}。A字廓形显瘦，百搭上装，轻松演绎优雅气质。",
        "仙气十足的{style}裙摆设计，{material}面料柔软亲肤，穿上即刻变身温柔仙女。",
    ],
    "外套": [
        "{material}外套，{fit}版型，兼顾保暖与时尚。{style}风格设计，无论休闲还是通勤均可驾驭。",
        "经典{style}款式，{material}面料，挺括有型。内搭T恤毛衣均可，{season}必备百搭外套。",
        "时尚{style}风格外套，{material}质地，轻薄不臃肿。多口袋设计实用美观，出门必备。",
    ],
    "卫衣": [
        "宽松{fit}卫衣，柔软{material}面料，舒适保暖。{style}风格印花设计，休闲运动均适宜。",
        "经典{style}款卫衣，面料厚实柔软，上身质感满满。日常穿搭利器，简单有型。",
    ],
    "配饰": [
        "精致{style}风格配饰，工艺精良，彰显品位。搭配多种风格服装均可提升整体造型质感。",
        "百搭{style}设计，精选材质打造，细节考究，是送礼或自用的绝佳之选。",
    ],
}
DEFAULT_DESCS = [
    "精选优质面料，版型经典百搭，穿着舒适，是日常穿搭不可缺少的单品。",
    "时尚设计与舒适材质完美结合，展现独特个人风格。",
    "简约而不简单，细节精致，彰显品质生活态度。",
]

MATERIALS = ["纯棉", "棉质", "麻棉", "雪纺", "针织", "羊毛混纺", "聚酯纤维", "牛仔"]
FITS      = ["宽松", "修身", "直筒", "oversize", "合身"]
SEASONS   = ["春夏", "秋冬", "四季", "夏季", "冬季"]
NECKS     = ["圆领", "V领", "方领", "高领", "翻领"]

def gen_desc(category, style):
    templates = DESC_TEMPLATES.get(category, DEFAULT_DESCS)
    tpl = random.choice(templates)
    try:
        return tpl.format(
            material=random.choice(MATERIALS),
            fit=random.choice(FITS),
            season=random.choice(SEASONS),
            neck=random.choice(NECKS),
            style=style or "时尚",
        )
    except KeyError:
        return random.choice(DEFAULT_DESCS)


def collect_image_urls(limit=8000):
    """从 Amazon metadata 提取真实服装图片 URL"""
    print(f"📂 读取 Amazon metadata：{META_FILE}")
    urls = []

    def try_parse(line):
        line = line.strip()
        if not line:
            return None
        # 先尝试标准 JSON
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            pass
        # 再尝试 Python dict 格式（旧版 Amazon 数据）
        try:
            return ast.literal_eval(line)
        except Exception:
            return None

    with gzip.open(META_FILE, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if len(urls) >= limit:
                break
            item = try_parse(line)
            if item and item.get("imUrl"):
                img = item["imUrl"]
                # 过滤掉无法访问的无效链接（常见问题）
                if img.startswith("http") and "images-amazon.com" in img:
                    urls.append(img)

    print(f"✅ 成功提取 {len(urls)} 个真实服装图片 URL")
    return urls


def update_products(app, img_urls):
    print("🔄 开始更新 products 表…")
    with app.app_context():
        products = Product.query.all()
        random.shuffle(img_urls)  # 打乱，多样化分配

        for i, p in enumerate(products):
            # 分配 1-3 张图片（循环使用 img_urls）
            n_imgs = random.randint(1, 3)
            start  = (i * 3) % max(len(img_urls), 1)
            p.images = [img_urls[(start + j) % len(img_urls)] for j in range(n_imgs)]

            # 更新描述（仅当原描述是占位文字时）
            if not p.description or len(p.description) < 10:
                p.description = gen_desc(p.category, p.style)

            if i % 200 == 0:
                db.session.flush()
                print(f"  已更新 {i} / {len(products)} 条…")

        db.session.commit()
        print(f"✅ 全部 {len(products)} 条商品图片和描述已更新！")


if __name__ == "__main__":
    if not os.path.exists(META_FILE):
        print("❌ 找不到 Amazon metadata 文件，请先下载放入 data/raw/")
        sys.exit(1)

    app = create_app()
    img_urls = collect_image_urls(limit=8000)

    if not img_urls:
        print("⚠️  未能提取到图片 URL，可能是文件格式问题，跳过图片更新")
        sys.exit(1)

    update_products(app, img_urls)
    print("\n🎉 商品图片更新完成！刷新前端页面即可看到真实服装图片。")
