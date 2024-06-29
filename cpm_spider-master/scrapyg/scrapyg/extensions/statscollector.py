import os
import pymongo
import pymysql
from datetime import datetime, timedelta
from threading import Timer
from scrapy import signals
from scrapy.exceptions import NotConfigured
from dbutils.pooled_db import PooledDB


class ScrapygServerMongodbSupport:
    def __init__(self, settings):
        # 连接mongodb
        db_uri = settings.get('SCRAPYG_SERVER_DB_URI')
        db_name = settings.get('SCRAPYG_SERVER_DB')
        collection_name = settings.get('SCRAPYG_SERVER_JOB_TABLE')
        client = pymongo.MongoClient(db_uri)
        self.collection = client[db_name][collection_name]

    def up_date(self, job_id, data: dict):
        self.collection.update_one({'id': job_id}, {'$set': data})


class ScrapygServerMysqlSupport:
    def __init__(self, settings):
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=500,
            maxcached=20,
            blocking=True,
            host=settings.get('SCRAPYG_SERVER_DB_HOST'),
            port=settings.get('SCRAPYG_SERVER_DB_PORT'),
            user=settings.get('SCRAPYG_SERVER_DB_USER'),
            password=settings.get('SCRAPYG_SERVER_DB_PASSWORD'),
            database=settings.get('SCRAPYG_SERVER_DB'),
            charset='utf8mb4')
        self.db = self.pool.connection()
        self.cur = self.db.cursor()
        self.table = settings.get('SCRAPYG_SERVER_JOB_TABLE')

    def up_date(self, job_id, data: dict):
        sql_pre = 'update {} set {} where id=%s'
        data_str = ','.join(f"{key}=%s" for key in data.keys())
        sql = sql_pre.format(self.table, data_str)
        values = [v for v in data.values()]
        values.append(job_id)
        self.cur.execute(sql,values)
        self.db.commit()

    def close(self):
        self.cur.close()
        self.db.close()
        self.pool.close()


class SpiderStatsCollector:

    def __init__(self, crawler):
        self.crawler = crawler
        self.exit = False
        self.interval = crawler.settings.get('SCRAPYG_STATS_COLLECTOR_INTERVAL')
        db_type = crawler.settings.get('SCRAPYG_SERVER_DB_TYPE')
        if db_type == 'mongodb':
            self.db = ScrapygServerMongodbSupport(crawler.settings)
        elif db_type == 'mysql':
            self.db = ScrapygServerMysqlSupport(crawler.settings)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('SCRAPYG_STATS_COLLECTOR_ENABLED'):
            raise NotConfigured
        o = cls(crawler)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.engine_started, signal=signals.engine_started)
        crawler.signals.connect(o.engine_stopped, signal=signals.engine_stopped)
        return o

    def engine_started(self):
        Timer(self.interval, self.execute).start()

    def engine_stopped(self):
        self.exit = True

    def spider_opened(self, spider):
        self.job_id = os.environ.get('SCRAPY_JOB')
        spider.crawler.stats.set_value('start_time', datetime.now())

    def spider_closed(self, spider):
        spider.crawler.stats.set_value('finish_time', datetime.now())

    def execute(self):
        stats_data = self.collect_stats()
        self.db.up_date(self.job_id, stats_data)
        if not self.exit:
            Timer(self.interval, self.execute).start()

    def collect_stats(self):
        stats = self.crawler.stats.get_stats()
        stats_data = {}
        # 启动时间
        start_time = stats.get('start_time')
        if start_time:
            stats_data['status'] = 'running'
            stats_data['start_time'] = start_time
        # 结束时间  scrapyd 强杀不会触发信号
        finish_time = stats.get('finish_time')
        if finish_time:
            stats_data['status'] = 'finished'
            # stats_data['end_time'] = finish_time + timedelta(hours=8)
            stats_data['end_time'] = finish_time
        # 请求数
        stats_data['request_num'] = stats.get('downloader/response_count', 0)
        # 待请求数量
        stats_data['request_waited'] = stats.get('scheduler/enqueued', 0) - stats.get('scheduler/dequeued', 0)
        # 爬取数据量
        stats_data['item_scraped'] = stats.get('item_scraped_count', 0)
        # 错误数量
        stats_data['error_num'] = stats.get('log_count/ERROR', 0)
        return stats_data
