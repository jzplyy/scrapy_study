import scrapy

class ProxyDownloaderMiddleware:
    def process_request(self, request:scrapy.Request, spider:scrapy.Spider):
        proxy_type = spider.crawler.settings.get('PROXY_TYPE',None)
        if proxy_type == 'fiddler':
            request.meta["proxy"] = 'http://localhost:8765'
        elif proxy_type == 'dynamic_proxy':
            request.meta["proxy"] = 'http://10.149.8.33:7700'
