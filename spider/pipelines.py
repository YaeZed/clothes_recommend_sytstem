"""
Scrapy Pipeline：将爬取的商品数据写入 MySQL
"""
import pymysql
from itemadapter import ItemAdapter


class MySQLPipeline:
    def open_spider(self, spider):
        import os
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
        self.conn = pymysql.connect(
            host     = os.getenv('DB_HOST', 'localhost'),
            port     = int(os.getenv('DB_PORT', 3306)),
            user     = os.getenv('DB_USER', 'root'),
            password = os.getenv('DB_PASSWORD', 'root'),
            db       = os.getenv('DB_NAME', 'clothes_recommend'),
            charset  = 'utf8mb4',
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        sql = """
            INSERT IGNORE INTO products (title, category, price, sales_count, images, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (
            adapter.get('title', ''),
            adapter.get('category', ''),
            float(adapter.get('price', 0) or 0),
            int(str(adapter.get('sales', '0')).replace('人付款', '').replace('+', '') or 0),
            str([adapter.get('image_url', '')]),
            adapter.get('description', ''),
        ))
        if self.cursor.rowcount % 100 == 0:
            self.conn.commit()
        return item
