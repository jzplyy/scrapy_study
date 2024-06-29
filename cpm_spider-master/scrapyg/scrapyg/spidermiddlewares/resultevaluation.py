from scrapy import signals
import datetime


class ResultEvaluationMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_closed(self, spider):
        # 结果评估
        if hasattr(spider, 'result_evaluation') and hasattr(spider, 'reschedule_date'):
            result_evaluation = spider.result_evaluation
            assert type(result_evaluation) == bool, 'result_evaluation must be bool'
            if not result_evaluation:
                # 重新调度日期
                reschedule_date = spider.reschedule_date
                assert type(reschedule_date) == datetime.datetime, 'reschedule_date must be datetime'
                spider.crawler.stats.set_value('reschedule_date', reschedule_date.strftime("%Y-%m-%d %H:%M:%S"))
            spider.crawler.stats.set_value('result_evaluation', str(result_evaluation).lower())