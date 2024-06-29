from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

import scrapy
import json

from scrapyg.models import BaseSpider

from cpm_spider.utils import aes_cipher, get_account_pwd


class CpmLogin(BaseSpider):
    """
    CPM - 登录
    """
    name = 'cpm_login'

    custom_settings = {
        'SPIDER_MIDDLEWARES': {},
        'ITEM_PIPELINES': {'scrapyg.pipelines.mongo.MongoCookiePipeline': 300}
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = kwargs['account']
        self.password = kwargs['pwd']

    def start_requests(self):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        }
        url = 'https://cpm.wuxibiologics.com/portalbasicapi/Access/Login'
        params = {
            "email": self.account,
            "password": aes_cipher(self.password),
            "returnUrl": "",
            "code": "",
            "language": "zh"
        }
        body = json.dumps(params)
        yield scrapy.Request(url, method='post', headers=headers, body=body)

    def parse(self, response, **kwargs):
        json_data = json.loads(response.text)
        if not json_data.get('isSuccess'):
            self.logger.error(response.text)
            return
        token = json_data.get('data').get('tokenAccess')
        data = {
            'domain': 'cpm.wuxibiologics.com',
            'account': self.account,
            'cookie': token,
            'cookie_info': '',
        }
        yield data


if __name__ == '__main__':
    from scrapyg.utils.utils import run_spider

    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
        # 'ITEM_PIPELINES': {},
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 3,
    }
    db_table = 'cpm'
    account, pwd = get_account_pwd()
    run_spider('cpm_login', proxy_type='', settings=custom_settings, db_table=db_table, account=account, pwd=pwd)
