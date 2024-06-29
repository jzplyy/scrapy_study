from scrapy.http.response import Response
from pyppeteer.page import Page, Response as PyppeteerResponse
from typing import List


class BrowserResponse(Response):
    close_page = True

    def __init__(self, *args, **kwargs):
        self.browser_tab: Page = kwargs.pop('browser_tab')
        self.response_list: List[PyppeteerResponse] = kwargs.pop('response_list')
        super().__init__(*args, **kwargs)
