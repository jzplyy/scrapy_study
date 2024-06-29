import scrapy
import time
from scrapy import signals
import uuid
import os
import datetime


class BaseSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    # 爬虫启动时间
    _job_start_time = None
    # 爬虫任务id
    _job_id = None

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for item in result:
            if isinstance(item, dict) or isinstance(item, scrapy.Item):
                # 当前爬虫实例id
                item['_job_id'] = self._job_id
                # 启动时间
                item['_job_start_time'] = self._job_start_time
                # 爬取时间
                item['_crawl_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
                # 爬取url
                item['_request_url'] = response.request.url
            yield item

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        self._job_id = os.environ.get('SCRAPY_JOB', uuid.uuid1().hex)
        spider.crawler.stats.set_value('start_time', datetime.datetime.now())
        spider.crawler.stats.set_value('_job_id', self._job_id)
        self._job_start_time = spider.crawler.stats.get_value('start_time').strftime("%Y-%m-%d %H:%M:%S")
        # spider.crawler.stats.set_value('_job_start_time', self._job_start_time)
        spider.logger.info('Spider opened: {} , _job_id: {} , _job_start_time: {}'.format(spider.name, self._job_id,
                                                                                      self._job_start_time))

    def spider_closed(self, spider):
        spider.crawler.stats.set_value('finish_time', datetime.datetime.now())