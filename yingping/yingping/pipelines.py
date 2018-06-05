# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi
from yingping.items import YingpingItem,shortcriticItem,longcriticItem


class YingpingPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        dbpool =adbapi.ConnectionPool('pymysql', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        self.dbpool.runInteraction(self.do_insert_info,item)
        self.dbpool.runInteraction(self.do_insert_shortcont,item)
        self.dbpool.runInteraction(self.do_insert_longcont,item)
        return item


    def do_insert_info(self,cursor,item):
        if isinstance(item,YingpingItem):
            try: 
                insert_movieinfo_sql, params = item.get_insert_movieinfo_sql()
                cursor.execute(insert_movieinfo_sql, params)
                print("电影详情插入成功")
            except:
                print("电影详情插入失败")

    def do_insert_shortcont(self,cursor,item):
        if isinstance(item, shortcriticItem):
            try:
                insert_short_content, shcn = item.get_insert_shortcn_sql()
                cursor.execute(insert_short_content,shcn)
                print("短评插入成功")
            except:
                print("短评插入失败")

    def do_insert_longcont(self,cursor,item):
        if isinstance(item, longcriticItem):

            try:
                insert_long_content,long = item.get_insert_longcn_sql()
                cursor.execute(insert_long_content,long)
                print("长评论插入成功")
            except:
                print("长评论插入失败")


