import asyncio
import sys
from urllib import parse
import logging
import time
from typing import Optional
from pyppeteer import launcher

# hook  禁用 防止监测webdriver
if '--enable-automation' in launcher.DEFAULT_ARGS:
    launcher.DEFAULT_ARGS.remove('--enable-automation')
import pyppeteer
from pyppeteer.browser import Browser
from pyppeteer.errors import PageError, TimeoutError
from scrapy.settings import Settings
from twisted.internet.defer import Deferred
import twisted.internet
from twisted.internet.asyncioreactor import AsyncioSelectorReactor
from urllib.parse import urlparse

from .browser_request import BrowserRequest
from .browser_response import BrowserResponse

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

reactor = AsyncioSelectorReactor(asyncio.get_event_loop())

# install AsyncioSelectorReactor
twisted.internet.reactor = reactor
sys.modules['twisted.internet.reactor'] = reactor

logger = logging.getLogger(__name__)


class ScrapyPyppeteerDownloaderMiddleware:
    """ Handles launching browser tabs, acts as a downloader.
    Probably eventually this should be moved to scrapy core as a downloader.
    """

    def __init__(self, settings: Settings):
        self._browser: Optional[Browser] = None
        self._launch_options = settings.get('PYPPETEER_LAUNCH', {})
        self._max_browser_tabs = int(settings.get('MAX_BROWSER_TABS', 10))
        self._page_lock = asyncio.Lock()
        self._download_timeout = float(settings.get('DOWNLOAD_TIMEOUT', 3 * 60))
        self._flow_lock = asyncio.Lock()
        self._flow = dict()
        self._download_delay_per_domain = float(settings.get('DOWNLOAD_DELAY'))

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler.settings)
        return s

    async def process_request(self, request, spider):
        if isinstance(request, BrowserRequest):
            return await self.process_browser_request(request)
        else:
            return

    async def process_browser_request(self, request: BrowserRequest):
        async with self._page_lock:
            if self._browser is None:
                self._browser = await pyppeteer.launch(self._launch_options)
            # 控制子页面数量
            while True:
                n_tabs = self._n_browser_tabs(self._browser)
                if n_tabs <= self._max_browser_tabs:
                    break
                else:
                    await asyncio.sleep(1)
            # 启动无痕模式
            # context = await self._browser.createIncognitoBrowserContext()
            # page = await context.newPage()
            page = await self._browser.newPage()
        # 设置默认参数
        await self._set_default_page_param(page)
        # 设置cookie，必须包含doman，否则不起作用
        await page.setCookie(*request.cookies)
        # 设置拦截-request
        enable_request_interception = request.meta.get('enable_request_interception', False)
        await page.setRequestInterception(enable_request_interception)
        intercept_request = request.meta.get('intercept_request')
        if intercept_request:
            intercept_request_kwargs = request.meta.get('intercept_request_kwargs', {})
            page.on('request', lambda req: asyncio.ensure_future(intercept_request(req, **intercept_request_kwargs)))
        elif enable_request_interception:
            page.on('request', lambda req: asyncio.ensure_future(self._intercept_request(req)))  # 必须传一个
        # 设置拦截-response
        intercept_response = request.meta.get('intercept_response')
        if intercept_response:
            page.on('response', lambda resp: asyncio.ensure_future(intercept_response(resp)))
        # 设置从页面返回的response
        condition_list = request.meta.get('wait_for_response_conditions')
        response_task_list = []
        if condition_list:
            for condition in condition_list:
                task = asyncio.ensure_future(page.waitForResponse(condition))
                response_task_list.append(task)
        try:
            url = parse.unquote(request.url)
            options = {
                'timeout': 1000 * self._download_timeout
            }
            # 限流
            await self._flow_control(url, self._download_delay_per_domain)
            # 请求页面
            await asyncio.wait([page.goto(url, options=options), page.waitForNavigation(options=options)])
            # 等待页面返回特定的response
            response_list = [await task for task in response_task_list]
            return BrowserResponse(url=page.url, browser_tab=page, response_list=response_list)
        except(PageError, TimeoutError) as e:
            await page.close()
            raise e

    async def process_exception(self, request, exception, spider):
        if isinstance(request, BrowserRequest):
            # 重试请求
            retry_times = request.meta.get('retry_times', 0)
            logger.warning('retry times:{} , {}'.format(retry_times, exception))
            max_retry_times = request.meta.get('max_retry_times', 2)
            if retry_times < max_retry_times:
                request.meta['retry_times'] = retry_times + 1
                return request

    async def _set_default_page_param(self, page):
        width, height = 1366, 768
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36')
        await page.setViewport({'width': width, 'height': height})
        await page.evaluateOnNewDocument("() => {Object.defineProperty(navigator, 'webdriver', {get: () => undefined})}")

    async def _intercept_request(self, req):
        await req.continue_()

    def _n_browser_tabs(self, browser: Browser) -> int:
        """ A quick way to get the number of browser tabs.
        """
        n_tabs = 0
        for context in browser.browserContexts:
            for target in context.targets():
                if target.type == 'page':
                    n_tabs += 1
        return n_tabs

    async def _flow_control(self, url, delay):
        domain = urlparse(url).netloc
        async with self._flow_lock:
            last_time = self._flow.get(domain, 0)
            while True:
                now = time.time()
                if now - last_time < delay:
                    await asyncio.sleep(0.5)
                else:
                    break
            self._flow[domain] = time.time()


class ScrapyPyppeteerSpiderMiddleware:

    def process_spider_exception(self, response, exception, spider):
        if isinstance(response, BrowserResponse):
            # 关闭页面
            Deferred.fromFuture(asyncio.ensure_future(self.close_page(response.browser_tab)))
            # 重试请求
            retry_times = response.request.meta.get('retry_times', 0)
            spider.logger.warning('retry times:{} , {}'.format(retry_times, exception))  # TODO 如何打印堆栈信息？
            max_retry_times = response.request.meta.get('max_retry_times', 2)
            if retry_times < max_retry_times:
                response.request.meta['retry_times'] = retry_times + 1
                return [response.request]

    def process_spider_output(self, response, result, spider):
        if isinstance(response, BrowserResponse):
            page = response.browser_tab
            if response.close_page:
                Deferred.fromFuture(asyncio.ensure_future(self.close_page(page)))
        for i in result:
            yield i

    async def close_page(self, page):
        try:
            await page.close()
        except Exception:
            pass
