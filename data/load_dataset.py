"""
数据集加载脚本：将公开数据集写入 MySQL
推荐数据集：Amazon Fashion（UCSD Recommender Systems）
下载地址：https://jmcauley.ucsd.edu/data/amazon/

使用方法：
  1. 下载 Clothing_Shoes_and_Jewelry 的 5-core reviews 和 metadata 文件
  2. 将文件放入 data/raw/ 目录
  3. 运行: python data/load_dataset.py
"""
import json
import sys
import os
import gzip
import random
import string

# 把项目根目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product
from backend.models.user import User
from backend.models.behavior import UserBehavior
from werkzeug.security import generate_password_hash

# ── 配置 ─────────────────────────────────────────────────────
RAW_DIR      = os.path.join(os.path.dirname(__file__), "raw")
META_FILE    = os.path.join(RAW_DIR, "meta_Clothing_Shoes_and_Jewelry.json.gz")
REVIEW_FILE  = os.path.join(RAW_DIR, "Clothing_Shoes_and_Jewelry_5.json.gz")
MAX_PRODUCTS = 5000   # 最多导入商品数量
MAX_REVIEWS  = 50000  # 最多导入行为数量

CATEGORY_MAP = {
    "Tops": "上衣", "Shirts": "上衣", "Blouses": "上衣",
    "Pants": "裤子", "Jeans":  "裤子", "Leggings": "裤子",
    "Dresses": "裙子", "Skirts": "裙子",
    "Coats": "外套", "Jackets": "外套", "Sweaters": "外套",
}
STYLE_LIST = ["休闲", "正式", "运动", "街头", "复古", "简约", "时尚"]


def parse_gz(filepath):
    """逐行解析 gzip JSON 文件"""
    with gzip.open(filepath, "rt", encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line.strip())
            except json.JSONDecodeError:
                continue


def load_products(app):
    print("[1/3] 正在导入商品数据...")
    asin_to_id = {}   # Amazon ASIN -> 本地 product_id
    count = 0

    with app.app_context():
        for item in parse_gz(META_FILE):
            if count >= MAX_PRODUCTS:
                break

            # 映射类目
            raw_cats   = item.get("categories", [[]])[0]
            category   = "其他"
            for raw in raw_cats:
                for k, v in CATEGORY_MAP.items():
                    if k.lower() in raw.lower():
                        category = v
                        break

            product = Product(
                title       = (item.get("title") or "未知商品")[:200],
                category    = category,
                style       = random.choice(STYLE_LIST),
                price       = float(item.get("price", "0").replace("$", "") or 0),
                sales_count = random.randint(10, 5000),
                images      = [item["imUrl"]] if item.get("imUrl") else [],
                description = item.get("description") or "",
                tags        = raw_cats[:5],
                attributes  = {
                    "brand":       item.get("brand", ""),
                    "asin":        item.get("asin", ""),
                },
            )
            db.session.add(product)

            # 每 500 条提交一次
            if count % 500 == 0:
                db.session.flush()
                print(f"  已处理 {count} 条商品...")

            asin_to_id[item.get("asin", "")] = product
            count += 1

        db.session.commit()
        print(f"  ✅ 商品导入完成，共 {count} 条")

    return asin_to_id


def load_users_and_behaviors(app, asin_to_id):
    print("[2/3] 正在导入用户与行为数据...")
    reviewer_map = {}   # reviewer_id -> User
    count = 0

    WEIGHT_TO_ACTION = {
        (0, 3):  "view",
        (3, 4):  "collect",
        (4, 5):  "cart",
        (5, 6):  "purchase",
    }

    def rating_to_action(rating):
        if rating <= 2: return "view"
        if rating == 3: return "collect"
        if rating == 4: return "cart"
        return "purchase"

    with app.app_context():
        for review in parse_gz(REVIEW_FILE):
            if count >= MAX_REVIEWS:
                break

            reviewer_id   = review.get("reviewerID", "")
            asin          = review.get("asin", "")
            overall       = review.get("overall", 3)

            if asin not in asin_to_id:
                continue

            # 自动创建用户
            if reviewer_id not in reviewer_map:
                rnd_suffix = "".join(random.choices(string.ascii_lowercase, k=4))
                user = User(
                    username   = f"user_{reviewer_id[-8:]}_{rnd_suffix}",
                    password   = generate_password_hash("password123"),
                    style_pref = random.sample(STYLE_LIST, 2),
                    size_info  = {"height": random.randint(155, 185),
                                  "weight": random.randint(45, 90)},
                )
                db.session.add(user)
                db.session.flush()
                reviewer_map[reviewer_id] = user

            user    = reviewer_map[reviewer_id]
            product = asin_to_id[asin]

            behavior = UserBehavior(
                user_id     = user.id,
                product_id  = product.id,
                action_type = rating_to_action(overall),
                duration    = random.randint(10, 300),
            )
            db.session.add(behavior)

            if count % 1000 == 0:
                db.session.flush()
                print(f"  已处理 {count} 条行为...")
            count += 1

        db.session.commit()
        print(f"  ✅ 用户与行为导入完成，共 {count} 条行为，{len(reviewer_map)} 位用户")


def create_admin(app):
    print("[3/3] 创建管理员账号（若不存在）...")
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username   = "admin",
                password   = generate_password_hash("admin123"),
                email      = "admin@example.com",
                role       = "admin",
            )
            db.session.add(admin)
            db.session.commit()
            print("  ✅ 管理员创建成功：admin / admin123")
        else:
            print("  ℹ️  管理员账号已存在，跳过")


if __name__ == "__main__":
    app = create_app()

    if not os.path.exists(META_FILE):
        print(f"❌ 找不到数据文件：{META_FILE}")
        print("请先下载 Amazon Fashion 数据集，放入 data/raw/ 目录")
        print("下载地址：https://jmcauley.ucsd.edu/data/amazon/")
        sys.exit(1)

    with app.app_context():
        db.create_all()

    asin_map = load_products(app)
    load_users_and_behaviors(app, asin_map)
    create_admin(app)
    print("\n🎉 数据集加载完成！")
