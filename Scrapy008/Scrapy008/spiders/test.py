# -*- coding: utf-8 -*-
import re
import scrapy
from urllib.parse import urljoin
from Scrapy008.items import Scrapy008Item

class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['book.douban.com']
    def start_requests(self):
        start_urls = 'https://book.douban.com/tag/童话?start=0&type=T'
        yield scrapy.Request(url=start_urls, callback=self.parse_detail)

    def parse_detail(self, response):
        for detail_url in response.xpath("//li[@class='subject-item']/div[2]/h2/a/@href").extract():
            yield scrapy.Request(url=detail_url, callback=self.parse)

        # next_page = response.xpath('//span[@class="next"]/a/@href').extract_first()
        # if next_page:
        #     next_url = response.urljoin(next_page)
        #     print('~~~~~~~~~~~~~~~~~%s~~~~~~~~~~~~~' % next_url)
        #     yield scrapy.Request(next_url, callback=self.parse_detail)

    def parse(self, response):
        item = Scrapy008Item()

        item['title'] = response.xpath('//*[@id="wrapper"]/h1/span/text()').extract_first(),
        item['author'] = response.css('div#info span.pl+a::text').extract_first(),  # 选择span的兄弟标签a
        item['chuban'] = re.search(r'<span.*?出版年.*?</span>\s*(.*?)<br/>', response.text).groups(1)[0],
        try:
            item['price'] = re.search(r'<span class="pl">定价:</span>\s(.*?)<br/>', response.text).groups(1)[0],
        except:
            item['price'] = None
        item['score'] = response.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract_first(),
        item['aurating_peoplethor'] = response.xpath('//a[@href="collections"]/span/text()').extract_first(),
        item['content'] = response.xpath('string(//div[@class="intro"])').extract_first()

        yield item
