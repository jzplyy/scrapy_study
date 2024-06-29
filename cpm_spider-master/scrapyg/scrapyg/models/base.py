import scrapy
import datetime


class BaseSpider(scrapy.Spider):
    # 数据库表名
    db_table: str = None
    # 数据库描述，只在mysql生效
    table_comment: str = None
    # 数据库字段映射，只有定义在其中的字段才会保存，只在mysql生效
    item_map: dict = None
    # 爬虫结果评估，默认True通过
    result_evaluation: bool = True
    # 重新调度日期,默认30分钟后
    reschedule_date = datetime.datetime.now() + datetime.timedelta(minutes=30)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        proxy_type = crawler.settings.get('PROXY_TYPE', None)
        if proxy_type == 'dynamic_proxy':
            crawler.settings['DOWNLOAD_HANDLERS'].update({
                'http': 'scrapyg.downloadhandler.NonPersistentDownloadHandler',
                'https': 'scrapyg.downloadhandler.NonPersistentDownloadHandler',
            })
        return super().from_crawler(crawler, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_table = kwargs.get('db_table',self.name)
