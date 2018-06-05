import scrapy
import re
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from yingping.items import YingpingItem,shortcriticItem,longcriticItem


class YinPin(CrawlSpider):
    name = "yingping"
    allowed_domains = ['movie.mtime.com','award.mtime.com']

    start_urls = ['http://movie.mtime.com/movie/list/index.html']

    rules = (
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/movie /list/index-\d+\.html',)),follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/list/\d+\.html')),follow=True),
        Rule(LinkExtractor(allow=(r'http://award.mtime.com/\d+/award/\d+/index.html')),follow=True),
        Rule(LinkExtractor(allow=(r'http://award.mtime.com/\d+/award/\d+/index-\d+\.html')), follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/$')), callback='movie_info', follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/reviews/short/new.html')),callback='short_critic_content',follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/reviews/short/new-\d+\.html')),callback='short_critic_content',follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/comment.html')),follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/comment-\d+\.html')),follow=True),
        Rule(LinkExtractor(allow=(r'http://movie.mtime.com/\d+/reviews/\d+\.html')),callback='long_critic_content',follow=True),
    )


    def movie_info(self, response):
        selector = Selector(response)
        movie_url = response.url
        number = re.compile(r'\d+')
        movie_num = int(number.search(str(movie_url)).group())
        movie_name = selector.xpath('//*[@id="db_head"]/div[2]/div/div[1]/h1/text()').extract_first()
        movie_release_time = selector.xpath('//*[@id="db_head"]/div[2]/div/div[1]/p[1]/a/text()').extract_first()
        movie_type = selector.xpath('//*[@id="db_head"]/div[2]/div/div[2]/a/text()').extract()
        if movie_type:
            movie_type_l = movie_type.pop()
        movie_type = ' '.join(movie_type)
        self.logger.info(response.url)
        item = YingpingItem(
            movie_num = movie_num,
            movie_name = movie_name,
            movie_release_time = movie_release_time,
            movie_type = movie_type,
        )
        yield item


    def short_critic_content(self, response):
        selector = Selector(response)
        movie_url = response.url
        number = re.compile(r'\d+')
        movie_num = int(number.search(str(movie_url)).group())
        short_contentsd = selector.css('#tweetRegion > dd > div > h3::text').extract()
        for shs in  short_contentsd:
            item = shortcriticItem(
                movie_num = movie_num,
                movie_scritic = shs,
            )
            yield item

    def long_critic_content(self,response):
        selector = Selector(response)
        movie_url = response.url
        number = re.compile(r'\d+')
        movie_num = int(number.search(str(movie_url)).group())
        critic_title = selector.css('.db_mediainner > h2::text').extract_first()
        critic_content = selector.css('.db_mediacont > p::text').extract()
        critic_string =  ''.join(critic_content)
        critic_string = critic_string.replace("\xa0","")
        critic_string = critic_string.replace("\u3000","")
        item = longcriticItem(
            movie_num = movie_num,
            movie_lcritic_title = critic_title,
            movie_lcritic = critic_string,
        )
        yield item
