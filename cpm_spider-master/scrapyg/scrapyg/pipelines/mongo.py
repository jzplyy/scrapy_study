from itemadapter import ItemAdapter
import pymongo
import datetime


class MongoCookiePipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_COOKIE_DATABASE', 'cookies'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if hasattr(spider, 'db_table') and spider.db_table is not None:
            self.mongo_collection = spider.db_table
        else:
            raise ValueError(f'{spider.name} must set db_table')

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _item = ItemAdapter(item).asdict()
        _item['time'] = time
        search = {
            'domain': _item['domain'],
            'account': _item['account'],
        }
        update = {
            '$set': {'cookie': _item['cookie'], 'time': time, 'cookie_info': _item['cookie_info']}
        }
        res = self.db[self.mongo_collection].find_one_and_update(search, update)
        if not res:
            self.db[self.mongo_collection].insert_one(_item)
        return item


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'scrapy_items'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if hasattr(spider, 'db_table') and spider.db_table is not None:
            self.mongo_collection = spider.db_table
        else:
            raise ValueError(f'{spider.name} must set db_table')

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.mongo_collection].insert_one(ItemAdapter(item).asdict())
        return item