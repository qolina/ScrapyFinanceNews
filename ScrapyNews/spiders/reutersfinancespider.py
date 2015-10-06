#-*- coding=utf-8 -*-
from scrapy import Spider
from scrapy import Selector
from scrapy.http import Request
from datetime import date,timedelta
from ScrapyNews.items import NewsItem
import re 

class ReutersFinanceSpider(Spider):
    name = 'reutersfinancespider'
    allowed_domains = ['reuters.com']

    start_categoryUrls = [
            "http://www.reuters.com/news/archive/businessNews?date=",
            "http://www.reuters.com/news/archive/USLegal?date=",
            "http://www.reuters.com/news/archive/innovationNews?date=",
            "http://www.reuters.com/news/archive/Aerospace?date=",
            "http://www.reuters.com/news/archive/banks?date=",
            "http://www.reuters.com/news/archive/autos?date=",
            "http://www.reuters.com/news/archive/ousivMolt?date=",
            "http://www.reuters.com/news/archive/marketsNews?date=",
            "http://www.reuters.com/news/archive/bondsNews?date=",
            "http://www.reuters.com/news/archive/usDollarRpt?date=",
            "http://www.reuters.com/news/archive/GCA-Commodities?date=",
            "http://www.reuters.com/news/archive/gc07?date=",
            "http://www.reuters.com/news/archive/retirement-news?date=",
            "http://www.reuters.com/topics/archive/fundsfundsNews?date="
    ]

    parsed_urls = []

    def __init__(self):
        super(ReutersFinanceSpider,self).__init__()
        self.reuters_url = 'http://www.reuters.com/'
        self.date_pattern = re.compile('([0-9]{4}/[0-9]{2}/[0-9]{2})')


    def start_requests(self):
        start_time = date(2015,04,10)
        end_time = date(2015,05,31)

        current_time = start_time

        while current_time <= end_time:
            for category_Url in self.start_categoryUrls:
                call_url = category_Url + current_time.strftime('%m%d%Y')
                yield Request(url=call_url,callback=self.parse_category)    
            current_time = current_time + timedelta(days=1)


    def parse_category(self, response):

        for href in response.xpath('//div[@class="feature"]/h2/a/@href'):
            url = href.extract()
            if not url.startswith("http://"):
                url =  self.reuters_url + url

#            print url
            yield Request(url, callback=self.parse_news)


    def parse_news(self,response):
        debug = False

        if response.url in self.parsed_urls:
            return
        self.parsed_urls.append(response.url)
        
        if debug:
            print "********************************************************************"
            print response.url

        newsItem = NewsItem()
        hxs = Selector(response)
        try:
            newsItem['news_title'] = hxs.xpath('//h1[@class="article-headline"]/text()').extract()[0]#.encode("utf-8")
            newsItem['news_authors'] = ", ".join(hxs.xpath('//div[@class="article-info"]/span[@class="byline"]/text()').extract())
            newsItem['news_posttime'] = hxs.xpath('//span[@class="timestamp"]/text()').extract()[0]#.encode("utf-8")
            first_paragraph = hxs.xpath('//span[@id="articleText"]/span[@class="focusParagraph"]/p/text()').extract()[0]
            left_content = "\n".join(hxs.xpath('//span[@id="articleText"]/p/text()').extract())
            newsItem['news_content'] = first_paragraph + "\n" + left_content


            newsItem['news_url'] = response.url
            newsItem['news_filename'] = response.url.rsplit('/',1)[1].strip(".html")

            post_date = self.date_pattern.search(response.url)
            
            if post_date is not None:
                newsItem['news_dir'] = post_date.group(1).replace("/", "-")

            newsItem['news_domain'] = "reuters"

            if debug:
                print "title", newsItem['news_title']
                print "authors", newsItem['news_authors']
                print "posttime", newsItem['news_posttime']
                print "content", newsItem['news_content']#[:20]
                print "dir", newsItem["news_dir"]
                print "filename", newsItem["news_filename"]

            yield newsItem
        except Exception,e:
            print '[ERROR]',e
