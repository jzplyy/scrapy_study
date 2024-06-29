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
from cpm_spider.utils import query_seed_from_quotation_header, aes_cipher, encrypt_data


class CpmPlasmidPreparationSequence(BaseSpider):
    """
    CPM - 报价单 - 质粒制备 - 序列信息
    """
    name = 'cpm_plasmid_preparation_sequence'

    table_comment = 'CPM - 报价单质粒制备序列信息'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'active_version': '发布版本',
        'data_id': '关联id',
        'theoretical_sequence_name': 'theoretical_sequence_name',
        'theoretical_sequence': 'theoretical_sequence',
        'remark': 'remark',
    }

    url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetPlasmidPreparationSequence?reportId={}&version={}'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        connection = pymongo.MongoClient(MONGO_URI)
        self.token = connection['cookies']['cpm'].find_one()['cookie']
        self.headers['Authorization'] = self.token
        self.seed_list = query_seed_from_quotation_header()
        self.public_key_path = kwargs['public_key_path']

    def start_requests(self):
        for id, quotation_code, active_version in self.seed_list:
            params = {}
            body = json.dumps(params)
            url = self.url_pre.format(quote(aes_cipher(id)), active_version)
            cb_kwargs = {
                'id': id,
                'quotation_code': quotation_code,
                'active_version': active_version,
            }
            yield scrapy.Request(url, method='post', headers=self.headers, body=body, cb_kwargs=cb_kwargs,
                                 dont_filter=True)

    def parse(self, response, **kwargs):
        id = kwargs['id']
        quotation_code = kwargs['quotation_code']
        active_version = kwargs['active_version']
        json_data = json.loads(response.text)
        if not json_data.get('isSuccess'):
            self.logger.error(response.text)
            return
        data_list = json_data.get('data', {}).get('pageData')
        data_list = json.loads(data_list)
        if not data_list:
            return
        for item in data_list:
            data_id = item.get('id')
            theoretical_sequence_name = item.get('TheoreticalSequenceName')
            theoretical_sequence = item.get('TheoreticalSequence')
            theoretical_sequence = encrypt_data(theoretical_sequence,
                                                self.public_key_path) if theoretical_sequence else ''
            remark = item.get('Remark')
            data = {
                'id': id,
                'quotation_code': quotation_code,
                'active_version': active_version,
                'data_id': data_id,
                'theoretical_sequence_name': theoretical_sequence_name,
                'theoretical_sequence': theoretical_sequence,
                'remark': remark,
            }
            yield data


if __name__ == '__main__':
    import os
    from scrapyg.utils.utils import run_spider

    custom_settings = {
        # 'LOG_LEVEL': 'DEBUG',
        # 'ITEM_PIPELINES': {},
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
    }
    public_key_path = os.path.join(BASE_DIR, 'cpm_spider/utils/public_key.pem')
    run_spider('cpm_plasmid_preparation_sequence', proxy_type='', settings=custom_settings,
               public_key_path=public_key_path)
