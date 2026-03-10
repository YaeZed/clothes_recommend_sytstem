"""
模拟数据生成器
生成真实感服装商品、用户、行为数据，用于开发和测试推荐算法
用法：.\\venv\\Scripts\\python data\\generate_mock_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
import json
from datetime import datetime, timedelta
from faker import Faker  # pip install faker
from werkzeug.security import generate_password_hash

fake = Faker('zh_CN')
random.seed(42)

# ─── 商品配置 ───────────────────────────────────────────────
CATEGORIES = ['上衣', '裤子', '裙子', '外套', '其他']
STYLES     = ['休闲', '正式', '运动', '街头', '复古', '简约', '时尚']
BRANDS     = ['ZARA', 'H&M', 'Uniqlo', '优衣库', 'Only', 'Vero Moda',
              'GU', 'Nike', 'Adidas', '太平鸟', 'Urban Revivo']

PRODUCT_NAMES = {
    '上衣': [
        '纯棉圆领T恤 {}风基础款', '宽松休闲卫衣 {}系长袖',
        '条纹POLO衫 {}款修身', '麻料短袖衬衫 {}轻薄透气',
        '印花短袖T恤 {}潮流美式',
    ],
    '裤子': [
        '直筒牛仔裤 {}款洗水', '工装多口袋裤 {}休闲',
        '运动束脚卫裤 {}宽松', '西装修身九分裤 {}商务',
        '格纹休闲阔腿裤 {}设计',
    ],
    '裙子': [
        'A字半身裙 {}高腰', '碎花系带连衣裙 {}法式',
        '百褶裙 {}复古小众', '针织吊带裙 {}性感',
        '牛仔半裙 {}休闲短款',
    ],
    '外套': [
        '双排扣毛呢大衣 {}优雅', '飞行员夹克 {}街头复古',
        '轻薄防风冲锋衣 {}户外', '翻领皮衣 {}机车风',
        '针织开衫 {}慵懒通勤',
    ],
    '其他': [
        '真丝睡衣套装 {}舒适', '运动套装 {}速干透气',
        '毛衣针织背心 {}叠穿', '工装连体裤 {}多口袋',
        '羽绒马甲 {}轻薄保暖',
    ],
}

# 平铺的随机图片（占位用，论文截图用真实图）
PLACEHOLDER_IMGS = [
    "https://picsum.photos/seed/{}/400/500",
]


def make_products(n=500):
    products = []
    for i in range(1, n + 1):
        cat   = random.choice(CATEGORIES)
        style = random.choice(STYLES)
        brand = random.choice(BRANDS)
        name_tmpl = random.choice(PRODUCT_NAMES[cat])
        title = brand + ' ' + name_tmpl.format(style)
        price = round(random.uniform(39, 999), 2)
        sales = random.randint(0, 5000)
        stock = random.randint(5, 500)
        imgs  = [PLACEHOLDER_IMGS[0].format(i + j * 100) for j in range(random.randint(1, 3))]
        tags  = random.sample(STYLES + CATEGORIES, k=random.randint(2, 4))
        products.append({
            'title':       title,
            'category':    cat,
            'style':       style,
            'price':       price,
            'stock':       stock,
            'sales_count': sales,
            'description': fake.text(max_nb_chars=150),
            'images':      json.dumps(imgs, ensure_ascii=False),
            'attributes':  json.dumps({
                'brand': brand,
                'color': random.choice(['白色','黑色','蓝色','红色','绿色','米色']),
                'size':  random.choice(['XS','S','M','L','XL','XXL']),
            }, ensure_ascii=False),
            'tags':        json.dumps(tags, ensure_ascii=False),
            'is_on_sale':  1,
        })
    return products


def make_users(n=200):
    users = []
    all_styles = STYLES[:]
    for i in range(1, n + 1):
        style_pref = random.sample(all_styles, k=random.randint(1, 3))
        users.append({
            'username': f'user_{i:04d}',
            'password': generate_password_hash('password123'),
            'email':    fake.email(),
            'role':     'admin' if i == 1 else 'user',
            'style_pref': json.dumps(style_pref, ensure_ascii=False),
            'size_info':  json.dumps({
                'height': random.randint(155, 185),
                'weight': random.randint(45, 90),
            }, ensure_ascii=False),
        })
    return users


def make_behaviors(user_ids, product_ids, n_behaviors=10000):
    ACTION_TYPES = ['view', 'collect', 'cart', 'purchase']
    ACTION_WEIGHTS = [0.6, 0.2, 0.1, 0.1]
    behaviors = []
    base_time = datetime.now() - timedelta(days=60)
    for _ in range(n_behaviors):
        uid  = random.choice(user_ids)
        pid  = random.choice(product_ids)
        act  = random.choices(ACTION_TYPES, weights=ACTION_WEIGHTS)[0]
        ts   = base_time + timedelta(seconds=random.randint(0, 60 * 24 * 3600))
        dur  = random.randint(5, 300) if act == 'view' else 0
        behaviors.append({
            'user_id':    uid,
            'product_id': pid,
            'action_type': act,
            'duration':   dur,
            'created_at': ts.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return behaviors


def run():
    import pymysql
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    load_dotenv(env_path)

    conn = pymysql.connect(
        host     = os.getenv('DB_HOST', 'localhost'),
        port     = int(os.getenv('DB_PORT', 3306)),
        user     = os.getenv('DB_USER', 'root'),
        password = os.getenv('DB_PASSWORD', 'root'),
        db       = os.getenv('DB_NAME', 'clothes_recommend'),
        charset  = 'utf8mb4',
        autocommit = False,
    )
    cur = conn.cursor()

    # ── 商品 ──────────────────────────────
    print("⏳ 写入商品数据...")
    products = make_products(500)
    cur.executemany("""
        INSERT INTO products
          (title,category,style,price,stock,sales_count,
           description,images,attributes,tags,is_on_sale)
        VALUES
          (%(title)s,%(category)s,%(style)s,%(price)s,%(stock)s,
           %(sales_count)s,%(description)s,%(images)s,%(attributes)s,%(tags)s,%(is_on_sale)s)
    """, products)
    conn.commit()
    cur.execute("SELECT id FROM products ORDER BY id")
    product_ids = [r[0] for r in cur.fetchall()]
    print(f"   ✅ 商品 {len(product_ids)} 条")

    # ── 用户 ──────────────────────────────
    print("⏳ 写入用户数据...")
    users = make_users(200)
    cur.executemany("""
        INSERT INTO users
          (username,password,email,role,style_pref,size_info)
        VALUES
          (%(username)s,%(password)s,%(email)s,%(role)s,%(style_pref)s,%(size_info)s)
    """, users)
    conn.commit()
    cur.execute("SELECT id FROM users ORDER BY id")
    user_ids = [r[0] for r in cur.fetchall()]
    print(f"   ✅ 用户 {len(user_ids)} 条  （管理员: user_0001 / password123）")

    # ── 行为 ──────────────────────────────
    print("⏳ 写入行为数据（10000条）...")
    behaviors = make_behaviors(user_ids, product_ids, 10000)
    # 分批写入
    batch = 500
    for start in range(0, len(behaviors), batch):
        cur.executemany("""
            INSERT INTO user_behaviors
              (user_id,product_id,action_type,duration,created_at)
            VALUES
              (%(user_id)s,%(product_id)s,%(action_type)s,%(duration)s,%(created_at)s)
        """, behaviors[start:start + batch])
        conn.commit()
    print(f"   ✅ 行为 {len(behaviors)} 条")

    cur.close()
    conn.close()
    print("\n🎉 模拟数据全部写入完成！")
    print("   管理员账号: user_0001 / password123")
    print("   下一步: 运行 notebooks/01_EDA.ipynb 进行数据探索")


if __name__ == '__main__':
    # 需要先安装 faker
    try:
        import faker
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'faker'], check=True)
    run()
