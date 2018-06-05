# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YingpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_name = scrapy.Field()  # 电影名称
    movie_num = scrapy.Field() # 电影编号
    movie_release_time = scrapy.Field()  # 上映时间
    movie_type = scrapy.Field()   #电影类型

    def get_insert_movieinfo_sql(self):
        insert_movieinfo_sql = """insert into yingping_movieinfo(movie_num,movie_name,movie_release_time,movie_type)values(%s,%s,%s,%s)"""
        params = (self["movie_num"], self["movie_name"], self["movie_release_time"], self["movie_type"])
        return insert_movieinfo_sql, params


class shortcriticItem(scrapy.Item):
    movie_num = scrapy.Field()  # 电影编号
    movie_scritic = scrapy.Field()  # 短影评
    print()

    def get_insert_shortcn_sql(self):
        insert_short_content = """insert into yingping_moviescritic(movie_num,movie_scritic)values(%s,%s)"""
        shcn = (self["movie_num"],self["movie_scritic"])
        return insert_short_content, shcn

class longcriticItem(scrapy.Item):
    movie_num = scrapy.Field()  # 电影编号
    movie_lcritic_title = scrapy.Field()  # 影评标题
    movie_lcritic = scrapy.Field()  # 长影评

    def get_insert_longcn_sql(self):
        insert_long_content ="""insert into yingping_                                                                                                                                                movielcritic(movie_num,movie_lcritic_title,movie_lcritic)values(%s,%s,%s)"""
        long = (self["movie_num"],self["movie_lcritic_title"],self["movie_lcritic"])
        return insert_long_content,long

