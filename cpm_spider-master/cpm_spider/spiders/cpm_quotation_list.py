from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import math

import scrapy
import json
import pymongo

from scrapyg.models import BaseSpider

from cpm_spider.settings import MONGO_URI


class CpmQuotationList(BaseSpider):
    """
    CPM - 报价单列表页
    """
    name = 'cpm_quotation_list'

    table_comment = 'CPM - 报价单列表页'

    item_map = {
        'id': 'id',
        'quotation_code': '编码',
        'user_name': '用户',
        'quotation_status': '状态',
        'wbp_code': 'WBP Code',
        'archive_date': '日期',
    }

    list_url = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetItems'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    }
    page_size = 100

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        connection = pymongo.MongoClient(MONGO_URI)
        self.token = connection['cookies']['cpm'].find_one()['cookie']
        self.headers['Authorization'] = self.token

    def start_requests(self):
        params = {
            "pageSize": self.page_size,
            "pageIndex": 1,
            "searchInfo": ""
        }
        body = json.dumps(params)
        yield scrapy.Request(self.list_url, method='post', headers=self.headers, body=body)

    def parse(self, response, **kwargs):
        json_data = json.loads(response.text)
        if not json_data.get('isSuccess'):
            self.logger.error(response.text)
            return
        # 发送分页请求
        total_num = json_data.get('pageInfo').get('totalCount')
        for i in range(2, math.ceil(total_num / self.page_size) + 1):
            params = {
                "pageSize": self.page_size,
                "pageIndex": i,
                "searchInfo": ""
            }
            body = json.dumps(params)
            yield scrapy.Request(self.list_url, method='post', headers=self.headers, body=body,
                                 callback=self.parse_list)
        # 提取本页数据
        for data in self.parse_list(response, **kwargs):
            yield data

    def parse_list(self, response, **kwargs):
        json_data = json.loads(response.text)
        if not json_data.get('isSuccess'):
            self.logger.error(response.text)
            return
        for item in json_data.get('data'):
            id = item.get('id')
            quotation_code = item.get('quotationCode')
            user_name = item.get('userName')
            quotation_status = item.get('quotationStatus')
            wbp_code = item.get('wbpCode')
            archive_date = item.get('archiveDate')
            data = {
                'id': id,
                'quotation_code': quotation_code,
                'user_name': user_name,
                'quotation_status': quotation_status,
                'wbp_code': wbp_code,
                'archive_date': archive_date,
            }
            yield data


if __name__ == '__main__':
    from scrapyg.utils.utils import run_spider

    custom_settings = {
        # 'LOG_LEVEL': 'DEBUG',
        # 'ITEM_PIPELINES': {},
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
    }
    run_spider('cpm_quotation_list', proxy_type='', settings=custom_settings)
