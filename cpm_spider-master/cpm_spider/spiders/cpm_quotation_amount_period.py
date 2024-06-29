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
from cpm_spider.utils import query_seed_from_quotation_header, aes_cipher


class CpmQuotationAmountPeriod(BaseSpider):
    """
    CPM - 报价单 - 合同金额和周期

    type映射关系：
    gene: "GeneSynthesis",
    pcr: "PCRCloning",
    mt: "PointMutation",
    pre: "PlasmidPrep"

    价格类型，js断点参数名称：
    this.publicPrice
    """
    name = 'cpm_quotation_amount_period'

    table_comment = 'CPM - 合同金额和周期'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'active_version': '发布版本',
        "SequenceName": "SequenceName",
        "ServicePriority": "ServicePriority",
        "type": "type",
        "PreparationAmount": "PreparationAmount",
        "IsServicePriority": "IsServicePriority",
        "EndotoxinLevel": "EndotoxinLevel",
        "GeneLength": "GeneLength",
        "ApiResult": "ApiResult",
        "IsAddPeriod": "IsAddPeriod",
        "IsCodonOptimization": "IsCodonOptimization",
        "IsPrice": "IsPrice",
        "IsReturn": "IsReturn",
        "IsError": "IsError",
        "Result": "Result",
        "hisResult": "hisResult",
    }

    url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetContractAmounAndPeriod?reportId={}&version={}'
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
        self.seed_list = query_seed_from_quotation_header()

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
        page_data = json_data['data']['pageData']
        page_data = json.loads(page_data)
        for item in page_data:
            data = {
                'id': id,
                'quotation_code': quotation_code,
                'active_version': active_version,
                "SequenceName": item.get('SequenceName'),
                "ServicePriority": item.get('ServicePriority'),
                "type":  item.get('type'),
                "PreparationAmount":  item.get('PreparationAmount'),
                "IsServicePriority":  item.get('IsServicePriority'),
                "EndotoxinLevel":  item.get('EndotoxinLevel'),
                "GeneLength":  item.get('GeneLength'),
                # "ApiResult":  item.get('ApiResult'),
                "IsAddPeriod":  item.get('IsAddPeriod'),
                "IsCodonOptimization": item.get('IsCodonOptimization'),
                "IsPrice":  item.get('IsPrice'),
                "IsReturn":  item.get('IsReturn'),
                "IsError": item.get('IsError'),
                "Result":  item.get('Result'),
                "hisResult":  item.get('hisResult'),
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
    run_spider('cpm_quotation_amount_period', proxy_type='', settings=custom_settings)
