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


class CpmPlasmidPreparationList(BaseSpider):
    """
    CPM - 报价单 - 质粒制备 - 列表数据
    """
    name = 'cpm_plasmid_preparation_list'

    table_comment = 'CPM - 报价单质粒制备列表数据'

    item_map = {
        'id': 'id',
        'quotation_code': '报价单号',
        'active_version': '发布版本',
        'data_id': '关联id',
        'sample_name': 'sample_name',
        'sample_type': 'sample_type',
        'preparation_amount': 'preparation_amount',
        'host': 'host',
        'endotoxin_level': 'endotoxin_level',
        'buffer_solution': 'buffer_solution',
        'dna_concentration': 'dna_concentration',
        'subpackage_tubes': 'subpackage_tubes',
        'plasmid_antibiotics': 'plasmid_antibiotics',
        'plasmid_length_bp': 'plasmid_length_bp',
        'level_plasmid_copy_number': 'level_plasmid_copy_number',
        'is_sequencing': 'is_sequencing',
        'sequencing_primer': 'sequencing_primer',
        'remark': 'remark',
    }

    url_pre = 'https://cpm.wuxibiologics.com/portaldatacollectionapi/GeneSynthesis/GetPlasmidPreparationList?reportId={}&version={}'
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
            sample_name = item.get('SampleName')
            sample_type = item.get('SampleType')
            preparation_amount = item.get('PreparationAmount')
            host = item.get('Host')
            endotoxin_level = item.get('EndotoxinLevel')
            buffer_solution = item.get('BufferSolution')
            dna_concentration = item.get('DNAConcentration')
            subpackage_tubes = item.get('SubpackageTubes')
            plasmid_antibiotics = item.get('PlasmidAntibiotics')
            plasmid_length_bp = item.get('PlasmidLength_bp')
            level_plasmid_copy_number = item.get('LevelPlasmidCopyNumber')
            is_sequencing = item.get('IsSequencing')
            sequencing_primer = item.get('SequencingPrimer')
            remark = item.get('Remark')
            data = {
                'id': id,
                'quotation_code': quotation_code,
                'active_version': active_version,
                'data_id': data_id,
                'sample_name': sample_name,
                'sample_type': sample_type,
                'preparation_amount': preparation_amount,
                'host': host,
                'endotoxin_level': endotoxin_level,
                'buffer_solution': buffer_solution,
                'dna_concentration': dna_concentration,
                'subpackage_tubes': subpackage_tubes,
                'plasmid_antibiotics': plasmid_antibiotics,
                'plasmid_length_bp': plasmid_length_bp,
                'level_plasmid_copy_number': level_plasmid_copy_number,
                'is_sequencing': is_sequencing,
                'sequencing_primer': sequencing_primer,
                'remark': remark,
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
    run_spider('cpm_plasmid_preparation_list', proxy_type='', settings=custom_settings)
    