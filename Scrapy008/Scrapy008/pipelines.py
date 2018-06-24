# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import re
import pymongo
import logging
import time
import pymysql.cursors
from twisted.enterprise import adbapi
import json
import codecs


class Scrapy008Pipeline(object):

    def __init__(self):
        self.time = time.time()

    def close_spider(self, spider):
        end_time = time.time()
        cha_time = end_time-self.time
        print('~~~~~~~~%f~~~~~~' % cha_time)   # 爬虫结束执行此函数，这里用来计时。
        # self.conn.close()

    def process_price(self, price):
        try:
            if re.match('\d+\.\d+元', price):    # 包含‘元’则去掉，没有则不作处理
                price = re.search('(.*?)元', price).group(1)
        except:
            logging.debug('item["price"] is no something')

        return float(price)

    def process_item(self, item, spider):
        try:
            if item.get('author'):
                item['author'] = item['author'][0].lstrip("\n").replace(' ', '').replace('\n', '').strip()  # 重复的去掉换行符和空格
        except:
            item['author'] = None

        item['price'] = self.process_price(item['price'][0])

        try:
            if item.get('score'):
                item['score'] = float(item['score'][0])
        except:
            item['score'] = None
        try:
            if item.get('aurating_peoplethor'):
                item['aurating_peoplethor'] = int(item['aurating_peoplethor'][0])
        except:
            item['aurating_peoplethor'] = None

        item['content'] = item['content'].replace('\n', '').strip()

        self.conn = pymysql.connect('localhost', 'root', '1234', 'mysql', charset='utf8')
        self.cur = self.conn.cursor()
        sql = """insert into doubanbook(title,author,chuban,price,score,aurating_peoplethor,content) VALUE (%s,%s,%s,%s,%s,%s,%s)"""
        self.cur.execute(sql, (item['title'],item['author'],item['chuban'],item['price'],item['score'],item['aurating_peoplethor'],item['content']))
        self.conn.commit()

        return item


class MongoPipeline():
    def __init__(self,mongo_url,mongodb):
        self.mongo_url = mongo_url
        self.mongodb = mongodb

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongodb=crawler.settings.get('MONGODB')
        )

    def open_spider(self, spider):
        self.conn = pymongo.MongoClient(self.mongo_url, 27017)
        self.db = self.conn[self.mongodb]

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.db.doubanbook.update({'title': item.get('title')}, {'$set': dict(item)}, True)
        #  用title去重，保证数据库中没有相同的title，第二个参数是表示用字典类型进行存储，True表示查询到了相同的title,则对那条数据进行更新，没有则添加
        return item


class JsonPipeline(object):
    def __init__(self):
        self.file = codecs.open('doubanbook.json', 'w', encoding='utf-8')  #  用codecs打开，可以避免一些繁杂的编码操作。

    def process_item(self, item,spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def close_spider(self):
        self.file.close()


# class MysqlTwistedPipline(object):
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):
#         dbparms = dict(
#             charset='utf-8',
#             use_unicode=True,
#             host=settings["MYSQL_HOST"],
#             db=settings["MYSQL_NAME"],
#             user=settings["MYSQL_USER"],
#             passwd=settings["MYSQL_PASSWD"],
#             cursorclass=pymysql.cursors.DictCursor,
#         )
#         dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         query = self.dbpool.runInteraction(self.do_insert, item)
#         query.addErrback(self.handle_error)
#         return item
#
#     def handle_error(self, failure):
#         print(failure)
#
#     def do_insert(self, cursor, item):
#         sql = """insert into doubanbook(title,author,chuban,price,score,aurating_peoplethor,content) VALUE (%s,%s,%s,%s,%s,%s,%s)"""
#         cursor.execute(sql, (item['title'], item['author'], item['chuban'], item['price'], item['score'], item['aurating_peoplethor'], item['content']))
