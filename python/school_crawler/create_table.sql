-- 실행: psql -U <user> -d <db> -f create_table.sql
CREATE TABLE IF NOT EXISTS pages (
  id SERIAL PRIMARY KEY,
  menu_cd VARCHAR(64),
  url TEXT NOT NULL,
  title TEXT,
  content TEXT,
  crawled_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE (menu_cd, url)
);
