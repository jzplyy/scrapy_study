from pathlib import Path
import sys
import os
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import scrapy
import json
import pymongo
from urllib.parse import quote

from scrapyg.models import BaseSpider
from cpm_spider.settings import MONGO_URI
from cpm_spider.utils import query_seed_from_quotation_list, aes_cipher


class CpmAdminQuotationFile(BaseSpider):
    """
    CPM - 管理后台 - 观数台填报 - 任务管理 - 任务监控
    """
    name = 'cpm_admin_quotation_file'

    table_comment = 'CPM管理后台 - 客户上传数据'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'file_path': '文件路径',
    }

    check_file_url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/TaskDone/CheckFile?Id={}'
    download_file_url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/TaskDone/DownFile?Id={}'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        connection = pymongo.MongoClient(MONGO_URI)
        self.token = connection['cookies']['cpm'].find_one()['cookie']
        self.headers['Authorization'] = self.token
        self.seed_list = query_seed_from_quotation_list()
        self.file_dir = kwargs['file_dir']

    def start_requests(self):
        for id, quotation_code in self.seed_list:
            url = self.check_file_url_pre.format(id)
            cb_kwargs = {
                'id': id,
                'quotation_code': quotation_code,
            }
            yield scrapy.Request(url, method='get', headers=self.headers, cb_kwargs=cb_kwargs, dont_filter=True)

    def parse(self, response, **kwargs):
        id = kwargs['id']
        json_data = json.loads(response.text)
        if json_data.get('message'):
            return
        url = self.download_file_url_pre.format(quote(aes_cipher(id)))
        yield scrapy.Request(url, method='get', headers=self.headers, cb_kwargs=kwargs, dont_filter=True,
                             callback=self.parse_file)

    def parse_file(self, response, **kwargs):
        id = kwargs['id']
        quotation_code = kwargs['quotation_code']
        file_content = response.body
        if file_content:
            resp_headers = response.headers
            filename_raw = str(resp_headers.get('Content-Disposition', ''))
            filename = re.search(".*filename=(.*?);.*", filename_raw).group(1)
            file_path = os.path.join(self.file_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            item = {
                'id': id,
                'quotation_code': quotation_code,
                'file_path': filename,
            }
            yield item


if __name__ == '__main__':
    from scrapyg.utils.utils import run_spider

    custom_settings = {
        # 'LOG_LEVEL': 'DEBUG',
        # 'ITEM_PIPELINES': {},
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
    }
    file_dir = os.path.join(BASE_DIR, 'files/_temp')
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    run_spider('cpm_admin_quotation_file', proxy_type='', settings=custom_settings, file_dir=file_dir)
