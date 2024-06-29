import scrapy


class BrowserRequest(scrapy.Request):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)