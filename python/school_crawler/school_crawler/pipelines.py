import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()  # optional .env support

class PostgresPipeline:
    def __init__(self):
        self.conn = None
        self.cur = None

    @classmethod
    def from_crawler(cls, crawler):
        # get connection info from env vars or settings
        pipeline = cls()
        pipeline.pg_host = os.getenv("PGHOST", crawler.settings.get("PGHOST", "localhost"))
        pipeline.pg_port = os.getenv("PGPORT", crawler.settings.get("PGPORT", 5432))
        pipeline.pg_db = os.getenv("PGDATABASE", crawler.settings.get("PGDATABASE", "postgres"))
        pipeline.pg_user = os.getenv("PGUSER", crawler.settings.get("PGUSER", "chatty"))
        pipeline.pg_password = os.getenv("PGPASSWORD", crawler.settings.get("PGPASSWORD", "1623"))
        return pipeline

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=self.pg_host,
            port=self.pg_port,
            dbname=self.pg_db,
            user=self.pg_user,
            password=self.pg_password
        )
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def process_item(self, item, spider):
        # upsert: insert or update content if already exists
        sql = """
        INSERT INTO pages (menu_cd, url, title, content)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (menu_cd, url)
        DO UPDATE SET title = EXCLUDED.title, content = EXCLUDED.content, crawled_at = now();
        """
        self.cur.execute(sql, (item.get('menu_cd'), item.get('url'), item.get('title'), item.get('content')))
        # commit is deferred until close; can call conn.commit() periodically if desired
        return item
