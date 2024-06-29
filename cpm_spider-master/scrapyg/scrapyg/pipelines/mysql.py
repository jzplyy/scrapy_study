from twisted.enterprise import adbapi

class MysqlPipeline(object):
    table_exists = False
    item_map = None
    table_comment = ''

    @classmethod
    def from_crawler(cls, crawler):
        cls.HOST = crawler.settings.get('MYSQL_HOST')
        cls.PORT = crawler.settings.get('MYSQL_PORT')
        cls.USER = crawler.settings.get('MYSQL_USER')
        cls.PASSWD = crawler.settings.get('MYSQL_PASSWORD')
        cls.DATABASE = crawler.settings.get('MYSQL_DATABASE')
        return cls()

    def open_spider(self, spider):
        self.dbparms = dict(
            host=self.HOST,
            port=self.PORT,
            user=self.USER,
            passwd=self.PASSWD,
            db=self.DATABASE,
            charset='utf8',
            cp_reconnect=True,
        )
        self.dbpool = adbapi.ConnectionPool("pymysql", **self.dbparms)
        if hasattr(spider, 'db_table') and spider.db_table is not None:
            self.db_table = spider.db_table
        else:
            raise ValueError(f'{spider.name} must set db_table')
        if hasattr(spider, 'item_map') and spider.item_map:
            default_items = {
                '_job_id': '任务id',
                '_job_start_time': '任务启动时间',
                '_crawl_time': '爬取时间',
                '_request_url': '请求url',
            }
            self.item_map = spider.item_map
            self.item_map.update(default_items)
        if hasattr(spider, 'table_comment'):
            self.table_comment = spider.table_comment

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入时的异常
        spider.logger.error('Mysql Error : %s , item : %s', failure, str(item))

    def close_spider(self, spider):
        # 关闭连接
        self.dbpool.close()

    def do_insert(self, cur, item):
        try:
            cur._connection._connection.ping()
        except:
            self.dbpool.close()
            self.dbpool = adbapi.ConnectionPool("pymysql", **self.dbparms)
        # 取出数据，执行cur sql
        _item = {}
        if self.item_map:
            for k, v in item.items():
                if k in self.item_map.keys():
                    _item[k] = v
        else:
            _item = item
        keys = ','.join(_item.keys())
        _values = ','.join(['%s' for _ in range(len(_item))])
        values = [v for v in _item.values()]
        if not self.table_exists:
            self.do_create(cur, item)
            self.table_exists = True
        sql_pre = 'INSERT INTO {} ({}) VALUES ({});'
        sql = sql_pre.format(self.db_table, keys, _values)
        cur.execute(sql,values)

    def do_create(self, cur, item):
        sql_pre = "CREATE TABLE IF NOT EXISTS {}(_id INT PRIMARY KEY AUTO_INCREMENT,{}) COMMENT='{}';"
        if self.item_map:
            col_names = ','.join("{} TEXT COMMENT '{}'".format(k, v) for k, v in self.item_map.items())
        else:
            col_names = ','.join("{} TEXT".format(k) for k in item.keys())
        sql = sql_pre.format(self.db_table, col_names, self.table_comment)
        cur.execute(sql)