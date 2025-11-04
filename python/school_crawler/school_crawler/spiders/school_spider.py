import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin, urlparse, parse_qs
from school_crawler.items import PageItem

class SchoolSpider(scrapy.Spider):
    name = "school"
    allowed_domains = ["onestop.pusan.ac.kr"]
    login_page = "https://onestop.pusan.ac.kr/login"
    base_page = "https://onestop.pusan.ac.kr/page"

    custom_settings = {
        # 필요시 개별 설정 오버라이드
    }

    def __init__(self, username=None, password=None, menu_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 자격증명은 -a username=... -a password=... 또는 환경변수로 전달
        import os
        self.username = username or os.getenv("ONESTOP_USER")
        self.password = password or os.getenv("ONESTOP_PASS")
        # 메뉴 목록: 쉼표로 구분하거나 None -> 기본 예시 하나
        if menu_list:
            self.menu_list = menu_list.split(",")
        else:
            # 예시: 기본 테스트용 메뉴코드 (사용자 필요에 따라 늘리기)
            self.menu_list = ["000000000000249"]

    def start_requests(self):
        # 먼저 로그인 페이지 GET (CSRF 토큰 확보)
        yield scrapy.Request(self.login_page, callback=self.parse_login_page)

    def parse_login_page(self, response):
        # 파싱해서 숨겨진 토큰(input hidden) 자동 추출 (common names 포함)
        soup = BeautifulSoup(response.text, "lxml")
        form = soup.find("form")
        # form action이나 필드명은 실제 페이지에 따라 조정해야 함
        form_action = self.login_page
        if form and form.get("action"):
            # 절대경로로 변환
            form_action = urljoin(response.url, form.get("action"))

        # 자동으로 숨겨진 input들 수집
        payload = {}
        for inp in soup.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            value = inp.get("value", "")
            payload[name] = value

        # 덮어쓰기: username/password 필드 이름이 'username','password'가 아닐 수 있음.
        # 흔한 폼필드 후보 목록(필요시 추가)
        replaced = False
        for uname_field in ("username", "userid", "user_id", "userId", "login_id", "id"):
            if uname_field in payload:
                payload[uname_field] = self.username
                replaced = True
                break
        if not replaced:
            # fallback: 새 필드 추가 (서버가 허용하면)
            payload["userid"] = self.username

        replaced = False
        for pwd_field in ("password", "passwd", "pass", "user_pw"):
            if pwd_field in payload:
                payload[pwd_field] = self.password
                replaced = True
                break
        if not replaced:
            payload["password"] = self.password

        # POST로 로그인
        self.logger.info("Attempting login to %s", form_action)
        yield scrapy.FormRequest(
            url=form_action,
            formdata=payload,
            callback=self.after_login,
            dont_filter=True
        )

    def after_login(self, response):
        # 로그인 성공 판별: 응답 HTML에 로그인 실패 메시지 혹은 로그아웃 링크 존재 여부 체크
        if "로그인" in response.text and "로그아웃" not in response.text and "logout" not in response.text.lower():
            self.logger.warning("Login may have failed — check credentials or form fields.")
            # 그래도 계속 시도하되, 실제 페이지 접근에서 상태코드 체크
        else:
            self.logger.info("Login seemed successful (check manually).")

        # 이제 메뉴 목록 페이지로 이동
        for menu_cd in self.menu_list:
            url = f"{self.base_page}?menuCD={menu_cd}"
            yield scrapy.Request(url, callback=self.parse_menu_page, meta={"menu_cd": menu_cd})

    def parse_menu_page(self, response):
        menu_cd = response.meta.get("menu_cd")
        soup = BeautifulSoup(response.text, "lxml")

        # 페이지별로 title, 본문 추출 로직을 조정하세요.
        # 일반적으로 <h1> 또는 <div class="content"> 등에서 추출.
        title = None
        if soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        else:
            # fallback: title 태그
            if soup.title:
                title = soup.title.get_text(strip=True)

        # content: 페이지에서 본문으로 보이는 주요 영역 선택 (아래는 범용 fallback)
        content_el = soup.find("div", {"class": "content"}) or soup.find("div", {"id": "content"}) or soup.find("article")
        if content_el:
            content = content_el.get_text(separator="\n", strip=True)
        else:
            # 전 페이지 텍스트를 기본으로 사용하되, 필요시 정교화
            content = soup.get_text(separator="\n", strip=True)

        item = PageItem()
        item["menu_cd"] = menu_cd
        item["url"] = response.url
        item["title"] = title
        item["content"] = content
        yield item
