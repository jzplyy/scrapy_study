from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from twisted.internet import reactor
from twisted.web.client import HTTPConnectionPool


class NonPersistentDownloadHandler(HTTPDownloadHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pool = HTTPConnectionPool(reactor, persistent=False)
