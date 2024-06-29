import os.path
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


class CpmQuotationGeneSynthesis(BaseSpider):
    """
    CPM - 报价单 - 基因合成

    https://cpm.wuxibiologics.com/client/#/about/quotation/details/762/SHYMYY-20221018004/4?v=1
    """
    name = 'cpm_quotation_gene_synthesis'

    table_comment = 'CPM - 报价单基因合成'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'active_version': '发布版本',
        'data_id': '关联id',
        'sequence_name': '序列名称',
        'sequence_type': '序列类型',
        'is_optimize': '是否密码子优化',
        'original_sequence': '原始序列',
        'regex_sequence': '校验后序列',
        'opted_seq': '密码子优化后序列',
    }

    url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetGeneSynthesisSequenceList?reportId={}&version={}'
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
        data_list = json_data.get('data')
        if not data_list:
            return
        for item in data_list:
            data_id = item.get('id')
            sequence_name = item.get('sequenceName')
            sequence_type = item.get('sequenceType')
            is_optimize = item.get('isCodonOptimization')
            original_sequence = item.get('originalSequence')
            original_sequence = encrypt_data(original_sequence, self.public_key_path) if original_sequence else ''
            regex_sequence = item.get('regexSequence')
            regex_sequence = encrypt_data(regex_sequence, self.public_key_path) if regex_sequence else ''
            opted_seq = item.get('opted_seq')
            opted_seq = encrypt_data(opted_seq, self.public_key_path) if opted_seq else ''
            data = {
                'id': id,
                'quotation_code': quotation_code,
                'active_version': active_version,
                'data_id': data_id,
                'sequence_name': sequence_name,
                'sequence_type': sequence_type,
                'is_optimize': is_optimize,
                'original_sequence': original_sequence,
                'regex_sequence': regex_sequence,
                'opted_seq': opted_seq,
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
    public_key_path = os.path.join(BASE_DIR, 'cpm_spider/utils/public_key.pem')
    run_spider('cpm_quotation_gene_synthesis', proxy_type='', settings=custom_settings, public_key_path=public_key_path)
