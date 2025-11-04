import scrapy
from bs4 import BeautifulSoup
from school_crawler.items import PageItem
from datetime import datetime

class SchoolSpider(scrapy.Spider):
    name = "school"
    allowed_domains = ["cse.pusan.ac.kr"]
    start_urls = ["https://cse.pusan.ac.kr/cse/14651/subview.do"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        posts = soup.select("table.artclTable tbody tr")
        if not posts:
            self.logger.warning("⚠️ 게시글을 찾을 수 없습니다. 셀렉터를 확인하세요.")
            return

        for post in posts:
            title_tag = post.select_one("td._artclTdTitle a strong")
            if not title_tag:
                continue

            href = title_tag.get("href")  # 🔹 href가 없으면 None 반환
            full_url = response.urljoin(href) if href else None

            item = PageItem()
            item["menu_cd"] = "14651"
            item["url"] = full_url
            item["title"] = title_tag.get_text(strip=True)
            item["content"] = None
            item["crawled_at"] = datetime.now()

            print("💾 Saving item:", item["title"])
            yield item

            # 페이지네이션 (다음 페이지 링크 따라가기)
        next_page = soup.select_one("a.pg_next")
        if next_page and next_page.get("href"):
            yield response.follow(next_page["href"], callback=self.parse)