"""
export_csv.py  ——  从 MySQL 导出 notebooks 所需的 CSV 文件
"""
import pymysql, os, csv
from dotenv import load_dotenv

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
os.makedirs("data/csv", exist_ok=True)

# ── ratings.csv ───────────────────────────────────────────────────
WEIGHTS = {"view": 0.2, "collect": 0.4, "cart": 0.6, "purchase": 1.0}
cur.execute("SELECT user_id, product_id, action_type FROM user_behaviors")
agg = {}
for uid, pid, act in cur.fetchall():
    key = (uid, pid)
    w = WEIGHTS.get(act, 0.2)
    if agg.get(key, 0) < w:
        agg[key] = w

with open("data/csv/ratings.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "product_id", "rating"])
    for (uid, pid), r in agg.items():
        writer.writerow([uid, pid, r])
print(f"ratings.csv: {len(agg)} rows")

# ── products.csv ──────────────────────────────────────────────────
cur.execute("SELECT id, title, category, style, price, sales_count FROM products")
prods = cur.fetchall()
with open("data/csv/products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["product_id", "title", "category", "style", "price", "sales_count"])
    writer.writerows(prods)
print(f"products.csv: {len(prods)} products")

# ── users.csv ─────────────────────────────────────────────────────
cur.execute('SELECT id, username FROM users WHERE role = "user"')
users = cur.fetchall()
with open("data/csv/users.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "username"])
    writer.writerows(users)
print(f"users.csv: {len(users)} users")

cur.close()
conn.close()
print("Done! CSV files updated. Ready to re-run notebooks.")
