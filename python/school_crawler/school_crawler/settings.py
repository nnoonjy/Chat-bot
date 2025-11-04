# Scrapy settings for onestop_crawler project
BOT_NAME = "school_crawler"

SPIDER_MODULES = ["school_crawler.spiders"]
NEWSPIDER_MODULE = "school_crawler.spiders"

# obey robots.txt? 권한을 확인했다면 True 권장, 개발 중이면 False (법적문제 주의)
ROBOTSTXT_OBEY = False

# 기본 headers
USER_AGENT = "onestop-bot/1.0 (+https://your.site)"

# 동시성/딜레이: 사이트에 부담을 주지 않도록 적절히 설정
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.0

# 쿠키 유지(로그인 세션 유지 위해 필요)
COOKIES_ENABLED = True

# 파이프라인 등록
ITEM_PIPELINES = {
    "school_crawler.pipelines.PostgresPipeline": 300,
}

# 로깅
LOG_LEVEL = "INFO"
