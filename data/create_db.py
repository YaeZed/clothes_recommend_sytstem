"""
一键初始化数据库脚本
用法: .\\venv\\Scripts\\python data\\create_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pymysql
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

host     = os.getenv('DB_HOST',     'localhost')
port     = int(os.getenv('DB_PORT', '3306'))
user     = os.getenv('DB_USER',     'root')
password = os.getenv('DB_PASSWORD', 'root')
db_name  = os.getenv('DB_NAME',     'clothes_recommend')

print(f"正在连接 MySQL: {user}@{host}:{port} ...")

try:
    # 先不指定数据库，连接 MySQL 服务器
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        f"DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ 数据库 [{db_name}] 创建成功！")
except pymysql.err.OperationalError as e:
    print(f"❌ 连接失败: {e}")
    print("请检查：")
    print("  1. MySQL 服务是否启动")
    print("  2. backend/.env 中 DB_PASSWORD 是否正确")
    sys.exit(1)

# 让 Flask app 自动创建所有数据表
print("正在创建数据表...")
from backend.app import create_app
from backend.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ 所有数据表创建成功！")

print("\n🎉 数据库初始化完成！")
print(f"   数据库: {db_name}")
print(f"   下一步: .\\venv\\Scripts\\python run.py  (启动后端)")
