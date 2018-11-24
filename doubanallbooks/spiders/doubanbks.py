#-*- coding: utf-8 -*-
import scrapy
import urllib
import io
import sys
from scrapy.http import Request,FormRequest
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

class DoubanbksSpider(scrapy.Spider):
    name = 'doubanbks'
    allowed_domains = ['douban.com']
    headers = {"User-Agent:": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}

    def start_requests(self):
        return [Request('https://accounts.douban.com/login',headers=self.headers, meta={'cookiejar':1},
                      callback=self.parse)]

    def parse(self, response):#得到标签页面下每个标签的地址
        img_href = response.xpath("//img[@id='captcha_image']/@src").extract_first()
        img_id = response.xpath("//input[@name='captcha-id']/@value").extract_first()
        print(img_href)
        print("请输入验证码")
        yanzheng = input()
        data = {
            'source':'None',
            'redir':"https://book.douban.com/tag/",
            'form_email': 'seaofhymn@sina.com',
            'form_password':'172542qy',
            'captcha-solution':yanzheng,
            'captcha-id':img_id}
        print(data)
        return [FormRequest.from_response(response,
                                          # url='https://accounts.douban.com/login',  # 真实post地址
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          formdata=data,
                                          headers = self.headers,
                                          callback=self.next,
                                          )]

    def next(self,response):
        tag_hrefs= []
        tmp_hrefs= response.xpath("//div[@id ='content']//table[@class='tagCol']//a/@href").extract()
        for tmp_href in tmp_hrefs:
            tmp_href=urllib.parse.urljoin(response.url,tmp_href)
            tag_hrefs.append(tmp_href)
            print(tmp_href)
        for tag_href in tag_hrefs:
            yield Request(tag_href,meta={'cookiejar':True},callback=self.parse_book_list)
            # yield scrapy.Request(tag_href,meta={'cookiejar':1}, callback=self.parse_book_list)
    def parse_book_list(self,response):#进入标签页面后处理页面里书籍列表,处理书籍的信息
        next_url=response.xpath("//span[@class='next']/a/@href").extract_first()
        next_url = urllib.parse.urljoin(response.url, next_url)
        book_lists=response.xpath("//div[@id='subject_list']//li")
        # item = {}
        for book in book_lists:
            item = {}
            item["name"]=book.xpath("./div[2]/h2/a/@title").extract_first()
            item["pub"]=book.xpath(".//div[2]/div[@class='pub']/text()").extract_first()
            item["href"]=book.xpath(".//div[@class='info']/h2/a/@href").extract_first()
            item["rk"] = book.xpath("./div[2]/div[@class='star clearfix']/span[@class='rating_nums']/text()").extract_first()
            item["peo"] = book.xpath("./div[2]/div[@class='star clearfix']/span[@class='pl']/text()").extract_first()
            item["cookie1"] =response.request.headers.getlist('Cookie')
            yield Request(item["href"],callback=self.parse_details,meta={"item":item,'cookiejar':True})
        yield Request(next_url,meta={'cookiejar':True},callback = self.parse_book_list)#翻页

    def parse_details(self,response):
        href = response.xpath("//a/@href").extract()[2]
        print(href)
        item = response.meta["item"]
        item["cookie2"] = response.request.headers.getlist('Cookie')
        item["desript"] = response.xpath("//div[@class ='related_info']//div[@class ='intro']/p/text()").extract()
        # print(item)
        yield item
