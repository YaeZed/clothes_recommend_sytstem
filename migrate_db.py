import pymysql
import os
from dotenv import load_dotenv

# 加载后端环境变量以获取数据库连接信息
load_dotenv('backend/.env')

def migrate():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            db=os.getenv('DB_NAME', 'clothes_recommend'),
            charset='utf8mb4'
        )
        cur = conn.cursor()
        
        # 定义需要添加的列
        columns_to_add = [
            ('nickname', 'VARCHAR(50) DEFAULT ""'),
            ('phone', 'VARCHAR(20) DEFAULT ""'),
            ('birthday', 'VARCHAR(20) DEFAULT ""'),
            ('avatar', 'VARCHAR(255) DEFAULT ""'),
            ('addresses', 'JSON')
        ]
        
        # 获取现有列名
        cur.execute("SHOW COLUMNS FROM users")
        existing_columns = [row[0] for row in cur.fetchall()]
        
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column {col_name}...")
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"Column {col_name} added.")
            else:
                print(f"Column {col_name} already exists.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
