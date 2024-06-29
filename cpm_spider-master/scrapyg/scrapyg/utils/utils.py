from urllib import parse
import asyncio
import types
import scrapy
from scrapy.cmdline import execute


def cookie_str_to_dict(cookie_str):
    """
    cookie字符串转换成python dict
    """
    cookies = dict([l.strip().split("=", 1) for l in cookie_str.split(";")])
    return cookies


def put_url_params(url: str, params: dict):
    """
    GET请求url参数拼接
    """
    return '?'.join([url, parse.urlencode(params)])


def after_sleep(sec):
    """
    @Decorator: asyncio sleep for coroutine or generator
    """
    def wrapper(function):
        def decorated(*args, **kwargs):
            function_instance = function(*args, **kwargs)
            if isinstance(function_instance, types.AsyncGeneratorType):
                async def inner():
                    try:
                        async for v in function_instance:
                            yield v
                    finally:
                        await asyncio.sleep(sec)
            else:
                async def inner():
                    try:
                        res = await function_instance
                        return res
                    finally:
                        await asyncio.sleep(sec)
            return inner()
        return decorated
    return wrapper


def run_spider(spider_name,proxy_type=None,settings=dict(),**kwargs):
    """
    run scrapy spider
    :param spider_name:scrapy.Spider.name
    :param proxy_type: 代理类型
    :param kwargs: 传递给爬虫的参数
    """
    cmd_list = [
        'scrapy', 'crawl',
        spider_name,
        '-s', 'PROXY_TYPE={}'.format(proxy_type),
    ]
    for key,value in settings.items():
        cmd_list.append('-s')
        cmd_list.append('{}={}'.format(key,value))
    for key,value in kwargs.items():
        cmd_list.append('-a')
        cmd_list.append('{}={}'.format(key,value))
    execute(cmd_list)


def update_request_body(request: scrapy.Request, data: dict):
    """
    更新scrapy.Request.body参数
    """
    body_str = str(request.body, encoding=request.encoding)
    formdata = {k: v for k, v in [(s.split('=')[0], s.split('=')[1]) for s in body_str.split('&')]}
    formdata.update(data)
    formdata_str = '&'.join([k + '=' + v for k, v in formdata.items()])
    _request = request.replace(body=formdata_str)
    return _request