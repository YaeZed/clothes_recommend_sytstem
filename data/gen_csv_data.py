"""
gen_csv_data.py
───────────────────────────────────────────────────────────────
从 MySQL 数据库导出真实数据到 CSV 文件供 notebooks 使用

用法: .\\venv\\Scripts\\python data\\gen_csv_data.py
输出: data/csv/ 目录下的 products.csv, users.csv, behaviors.csv
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from backend.app import create_app
from backend.extensions import db
from backend.models.product import Product
from backend.models.user import User
from backend.models.behavior import UserBehavior

OUT_DIR = os.path.join(os.path.dirname(__file__), 'csv')
os.makedirs(OUT_DIR, exist_ok=True)

app = create_app()
with app.app_context():
    # ─── 商品 ─────────────────────────────────────────────────────
    print('⏳ 从数据库导出商品数据...')
    products = Product.query.filter_by(is_on_sale=True).all()
    products_df = pd.DataFrame([{
        'id':          p.id,
        'title':       p.title,
        'category':    p.category,
        'style':       p.style,
        'price':       float(p.price) if p.price else 0,
        'stock':       p.stock,
        'sales_count': p.sales_count,
        'is_on_sale':  1 if p.is_on_sale else 0,
        'tags':        ','.join(p.tags) if p.tags else '',
    } for p in products])
    products_df.to_csv(os.path.join(OUT_DIR, 'products.csv'), index=False, encoding='utf-8-sig')
    print(f'   ✅ products.csv  ({len(products_df)} 行)')

    # ─── 用户 ─────────────────────────────────────────────────────
    print('⏳ 从数据库导出用户数据...')
    users = User.query.filter_by(role='user').all()
    users_df = pd.DataFrame([{
        'id':         u.id,
        'username':   u.username,
        'style_pref': ','.join(u.style_pref) if u.style_pref else '',
        'height':     (u.size_info or {}).get('height', 165),
        'weight':     (u.size_info or {}).get('weight', 55),
    } for u in users])
    users_df.to_csv(os.path.join(OUT_DIR, 'users.csv'), index=False, encoding='utf-8-sig')
    print(f'   ✅ users.csv     ({len(users_df)} 行)')

    # ─── 行为 ─────────────────────────────────────────────────────
    print('⏳ 从数据库导出行为数据...')
    behaviors = UserBehavior.query.order_by(UserBehavior.created_at).all()
    behaviors_df = pd.DataFrame([{
        'id':          b.id,
        'user_id':     b.user_id,
        'product_id':  b.product_id,
        'action_type': b.action_type,
        'duration':    b.duration,
        'created_at':  b.created_at.isoformat() if b.created_at else '',
    } for b in behaviors])
    behaviors_df.to_csv(os.path.join(OUT_DIR, 'behaviors.csv'), index=False, encoding='utf-8-sig')
    print(f'   ✅ behaviors.csv ({len(behaviors_df)} 行)')

print(f'\n🎉 CSV 文件已从 MySQL 导出到 data/csv/')
print('   接下来打开 notebooks/01_EDA.ipynb 开始数据探索')
