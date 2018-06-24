# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
from fake_useragent import UserAgent
from scrapy.exceptions import IgnoreRequest

class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, spider, request):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault(b'User-Agent', get_ua())

    def process_response(self, spider, request, response):
        if response.status in [300,301,302,303,403]:
            try:
                redirect_url = response.headers['location']
                if 'login' in redirect_url:
                    logging.warning('need login')
                    return None
            except:
                raise IgnoreRequest
        return response