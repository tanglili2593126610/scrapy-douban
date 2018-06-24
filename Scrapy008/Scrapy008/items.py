# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Scrapy008Item(scrapy.Item):

    title = scrapy.Field()
    author = scrapy.Field()
    chuban = scrapy.Field()
    price = scrapy.Field()
    score = scrapy.Field()
    aurating_peoplethor = scrapy.Field()
    content = scrapy.Field()