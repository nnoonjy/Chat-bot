import psycopg2
import os
from dotenv import load_dotenv

class PostgresPipeline:
    def __init__(self):
        load_dotenv()
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.cursor = self.connection.cursor()
        print("✅ Connected to PostgreSQL")

    def process_item(self, item, spider):
        print("💾 Saving item to DB:", item["title"])
        try:
            self.cursor.execute(
                """
                INSERT INTO pages (menu_cd, url, title, content, crawled_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    item["menu_cd"],
                    item["url"],
                    item["title"],
                    item["content"],
                    item["crawled_at"],
                ),
            )
            self.connection.commit()
        except Exception as e:
            print("❌ DB INSERT ERROR:", e)
            self.connection.rollback()  # 추가

        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
        print("🔒 PostgreSQL connection closed")
