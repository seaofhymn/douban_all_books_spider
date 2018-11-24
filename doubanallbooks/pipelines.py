# -*- coding: utf-8 -*-
from pymysql import *
import re
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html



class DoubanallbooksPipeline(object):
    def process_item(self, item, spider):
        # item["desript"] = item["desript"].replace()
        item["pub"] = item["pub"].replace("\n","")
        item["peo"] = item["peo"].replace("\n","")
        item["peo"] = item["peo"].strip()
        # item["peo"] = re.match("\d+",item["peo"]).group()
        item["desript"] = "".join(item["desript"])
        print(item)
        conn = connect(host='localhost', port=3306, user='root', password='123', database='douban', charset='utf8')
        cur1 = conn.cursor()
        sql = """insert into doubanall (name,pub,rk,peo,desript,href) values("%s","%s","%s","%s","%s","%s");""" %(item["name"], item["pub"], item["rk"], item["peo"], item["desript"],item["href"])
        # sql = """insert into doubandushu (name,rk,con,description,peo,author) values("%s","%s","%s","%s","%s","%s")""" % (
        # item["mv_name"], item["mv_rank"], item["content"], item["mv_desc"], item["peo_rank"], item["mv_author"])
        cur1.execute(sql)
        conn.commit()
        cur1.close()
        conn.close()
        return item
