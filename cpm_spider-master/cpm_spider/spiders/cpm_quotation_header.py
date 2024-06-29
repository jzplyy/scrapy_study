from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import scrapy
import json
import pymongo
from urllib.parse import quote

from scrapyg.models import BaseSpider
from cpm_spider.settings import MONGO_URI
from cpm_spider.utils import query_seed_from_quotation_list, aes_cipher


class CpmQuotationHeader(BaseSpider):
    """
    CPM - 报价单 - 首页
    """
    name = 'cpm_quotation_header'

    table_comment = 'CPM - 报价单首页'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'active_version': '发布版本',
        'customer': '委托方(甲方)',
        'customer_contacts': '联系人',
        'customer_phone': '电话',
        'customer_email': '电子邮件',
        'confirm_time': '确认时间',
        # 'service': '服务方(乙方)',
        'service_contacts': '联系人',
        'service_phone': '电话',
        'service_email': '电子邮件',
        'publish_time': '发布时间',
    }

    url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetHeaderItems?reportId={}&orderCode={}'
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

    def start_requests(self):
        for id, quotation_code in self.seed_list:
            params = {}
            body = json.dumps(params)
            url = self.url_pre.format(quote(aes_cipher(id)), quotation_code)
            cb_kwargs = {
                'id': id,
                'quotation_code': quotation_code,
            }
            yield scrapy.Request(url, method='post', headers=self.headers, body=body, cb_kwargs=cb_kwargs,
                                 dont_filter=True)

    def parse(self, response, **kwargs):
        id = kwargs['id']
        quotation_code = kwargs['quotation_code']
        json_data = json.loads(response.text)
        if not json_data.get('isSuccess'):
            self.logger.error(response.text)
            return
        confirm_data = json.loads(json_data['data']['confirmList'])
        if confirm_data:
            confirm_data = confirm_data[0]
        fsuser = json_data['data'].get('fSusers', {})
        user = json_data['data'].get('user', {})
        version_list = json.loads(json_data['data']['versionList'])
        active_version = 1
        if version_list:
            for item in version_list:
                if item.get('IsPublishVersion') == 'Y':
                    active_version = item.get('Version', 1)
        # 数据字段
        customer = json_data['data'].get('depment')
        customer_contacts = user.get('fullName') if user else ''
        customer_phone = user.get('phoneNumber') if user else ''
        customer_email = user.get('email') if user else ''
        confirm_time = confirm_data['EditTime'] if confirm_data else ''
        service_contacts = fsuser.get('fullName') if fsuser else ''
        service_phone = fsuser.get('phoneNumber') if fsuser else ''
        service_email = fsuser.get('email') if fsuser else ''
        publish_time = confirm_data['CreateTime'] if confirm_data else ''
        data = {
            'id': id,
            'quotation_code': quotation_code,
            'active_version': active_version,
            'customer': customer,
            'customer_contacts': customer_contacts,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'confirm_time': str(confirm_time).replace('T', ' ').replace('None', ''),
            'service_contacts': service_contacts,
            'service_phone': service_phone,
            'service_email': service_email,
            'publish_time': str(publish_time).replace('T', ' ').replace('None', ''),
        }
        yield data


if __name__ == '__main__':
    from scrapyg.utils.utils import run_spider

    custom_settings = {
        # 'LOG_LEVEL': 'DEBUG',
        # 'ITEM_PIPELINES': {},
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
    }
    run_spider('cpm_quotation_header', proxy_type='', settings=custom_settings)
