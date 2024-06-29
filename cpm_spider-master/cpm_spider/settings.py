# Scrapy settings for new_common_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'cpm_spider'

SPIDER_MODULES = ['cpm_spider.spiders']
NEWSPIDER_MODULE = 'cpm_spider.spiders'

RETRY_TIMES = 3

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 10000
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'scrapyg.spidermiddlewares.base.BaseSpiderMiddleware': 100,
   # 'scrapyg.scrapy_pyppeteer.ScrapyPyppeteerSpiderMiddleware': 1000,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'scrapyg.scrapy_pyppeteer.ScrapyPyppeteerDownloaderMiddleware': 1000,
   # 'scrapyg.downloadermiddlewares.proxy.ProxyDownloaderMiddleware': 350,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   # 'scrapyg.extensions.statscollector.SpiderStatsCollector': 500,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'scrapyg.pipelines.mongo.MongoPipeline': 300,
   'scrapyg.pipelines.mysql.MysqlPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 辅助数据库
MONGO_URI = 'mongodb://spider:sbdSpiMonAss@10.13.123.147:27017/cookies'
MONGO_DATABASE = 'scrapy_items'
MONGO_COOKIE_DATABASE = 'cookies'
MONGO_DUPEFILTER_DATABASE = 'scrapy_dupefilters'

# scrapyg_server数据库
# SCRAPYG_SERVER_DB_TYPE = 'mongodb'
# SCRAPYG_SERVER_DB_URI = 'mongodb://root:root@10.149.8.33:27017'
# SCRAPYG_SERVER_DB = 'scrapyg_server'
# SCRAPYG_SERVER_JOB_TABLE = 'core_job'

# scrapyg_server stats collector
# SCRAPYG_STATS_COLLECTOR_ENABLED = True
# SCRAPYG_STATS_COLLECTOR_INTERVAL = 5

# mysql
MYSQL_HOST = '10.13.123.147'
MYSQL_PORT = 3306
MYSQL_USER = 'spider'
MYSQL_PASSWORD = 'sbdSpSu20#'
MYSQL_DATABASE = 'spider'

# 日志
# LOG_LEVEL = 'DEBUG'  #  CRITICAL, ERROR, WARNING, INFO, DEBUG

# chrome webdriver path
# WEBDRIVER_PATH = 'D:/webdriver/chrome/chromium/chrome.exe'

# mongodb去重组件
MONGO_DUPEFILTER_ENABLED = True

# 代理
# PROXY = '127.0.0.1:7700'

# ============================================ 线上 ===============================================
LOG_LEVEL = 'INFO'
# WEBDRIVER_PATH = 'E:/webdriver/chrome/chromium/chrome.exe'
