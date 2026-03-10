"""
create_demo_users.py
创建 3 个预设演示账号，每个账号有不同的穿搭偏好，
并直接写入差异化的推荐数据（不需要重跑 notebooks）。

账号：
  fashionista  / demo123  偏好：裙子 / 外套  → 女装时尚风
  streetboy    / demo123  偏好：上衣 / 卫衣  → 街头运动风
  officelady   / demo123  偏好：外套 / 裤子  → 职场通勤风
"""

import pymysql, os, random
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

conn = pymysql.connect(
    host     = os.getenv("DB_HOST", "localhost"),
    port     = int(os.getenv("DB_PORT", 3306)),
    user     = os.getenv("DB_USER", "root"),
    password = os.getenv("DB_PASSWORD", "root"),
    db       = os.getenv("DB_NAME", "clothes_recommend"),
    charset  = "utf8mb4",
    connect_timeout = 10,
)
cur = conn.cursor()

# ── 演示用户配置 ──────────────────────────────────────────────────
DEMO_USERS = [
    {
        "username":   "fashionista",
        "password":   "demo123",
        "style_pref": '["时尚", "甜美"]',
        "fav_cats":   ["裙子", "外套"],   # 偏好类目
    },
    {
        "username":   "streetboy",
        "password":   "demo123",
        "style_pref": '["街头", "运动"]',
        "fav_cats":   ["上衣", "卫衣"],
    },
    {
        "username":   "officelady",
        "password":   "demo123",
        "style_pref": '["正式", "简约"]',
        "fav_cats":   ["外套", "裤子"],
    },
]

# ── 1. 创建用户 ────────────────────────────────────────────────────
user_ids = {}
for u in DEMO_USERS:
    cur.execute("SELECT id FROM users WHERE username=%s", (u["username"],))
    row = cur.fetchone()
    if row:
        uid = row[0]
        print(f"  用户 {u['username']} 已存在 (id={uid})，跳过创建")
    else:
        pw_hash = generate_password_hash(u["password"])
        cur.execute(
            "INSERT INTO users (username, password, style_pref, size_info, role, created_at) "
            "VALUES (%s, %s, %s, '{}', 'user', NOW())",
            (u["username"], pw_hash, u["style_pref"]),
        )
        conn.commit()
        uid = cur.lastrowid
        print(f"  ✅ 创建用户 {u['username']} (id={uid})")
    user_ids[u["username"]] = uid

# ── 2. 为每个用户写行为记录 & 个性化推荐 ──────────────────────────
ACTION_WEIGHTS = {"view": 0.2, "collect": 0.4, "cart": 0.6, "purchase": 1.0}

for u in DEMO_USERS:
    uid = user_ids[u["username"]]

    # 先删除该用户旧的行为和推荐
    cur.execute("DELETE FROM user_behaviors WHERE user_id=%s", (uid,))
    cur.execute("DELETE FROM recommendations WHERE user_id=%s", (uid,))

    # 取偏好类目的商品（优先类）& 其他类目（少量）
    fav_ph = ",".join(["%s"] * len(u["fav_cats"]))
    cur.execute(
        f"SELECT id FROM products WHERE category IN ({fav_ph}) ORDER BY sales_count DESC LIMIT 40",
        tuple(u["fav_cats"]),
    )
    fav_products = [r[0] for r in cur.fetchall()]

    cur.execute(
        f"SELECT id FROM products WHERE category NOT IN ({fav_ph}) ORDER BY RAND() LIMIT 20",
        tuple(u["fav_cats"]),
    )
    other_products = [r[0] for r in cur.fetchall()]

    # 写行为（偏好类：多次高权重行为；其他：浏览）
    behaviors = []
    for pid in fav_products:
        action = random.choice(["collect", "cart", "purchase"])
        behaviors.append((uid, pid, action, random.randint(60, 300)))
    for pid in other_products:
        behaviors.append((uid, pid, "view", random.randint(5, 30)))

    cur.executemany(
        "INSERT INTO user_behaviors (user_id, product_id, action_type, duration, created_at) "
        "VALUES (%s, %s, %s, %s, NOW())",
        behaviors,
    )

    # 直接写推荐结果（偏好类商品高分，其余低分）
    recs = []
    for i, pid in enumerate(fav_products[:20]):
        score = round(1.0 - i * 0.02, 3)  # 0.98 → 0.60
        recs.append((uid, pid, "hybrid", score))
    for i, pid in enumerate(other_products[:10]):
        score = round(0.35 - i * 0.01, 3)
        recs.append((uid, pid, "hybrid", score))

    cur.executemany(
        "INSERT INTO recommendations (user_id, product_id, algo_type, score, created_at) "
        "VALUES (%s, %s, %s, %s, NOW())",
        recs,
    )

    conn.commit()
    print(f"  ✅ {u['username']}: {len(behaviors)} 条行为, {len(recs)} 条推荐 | 偏好：{u['fav_cats']}")

cur.close()
conn.close()

print("\n" + "="*50)
print("演示账号创建完毕！登录密码均为 demo123")
print("="*50)
print("  fashionista  → 推荐以【裙子/外套】为主（女装时尚风）")
print("  streetboy    → 推荐以【上衣/卫衣】为主（街头运动风）")
print("  officelady   → 推荐以【外套/裤子】为主（职场通勤风）")
