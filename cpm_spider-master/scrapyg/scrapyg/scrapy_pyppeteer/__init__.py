# Public API https://github.com/lopuhin/scrapy-pyppeteer
from .browser_request import BrowserRequest
from .browser_response import BrowserResponse
from .middleware import ScrapyPyppeteerDownloaderMiddleware, ScrapyPyppeteerSpiderMiddleware

# Make pyppeteer and websockets less noisy with scrapy debug logging level
import logging

logging.getLogger('pyppeteer').setLevel(logging.INFO)
logging.getLogger('websockets.protocol').setLevel(logging.INFO)
del logging
