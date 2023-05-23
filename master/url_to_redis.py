# -*- coding: utf-8 -*-
# @Time    : 4/9/21 4:39 PM
# @Author  : wangjie
import init
import os
import time
import traceback
import redis
from multiprocessing import Process
from urllib.parse import urlparse
import mysqlUtil1
from config import Config
from ulogger import setLogger

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"urlToRedis")
crawl_config = Config().get_content("CRAWLER")
cache = redis.Redis(host=crawl_config.get("redis_host"), port=int(crawl_config.get("redis_port")), password=crawl_config.get("redis_pwd"), decode_responses=True, errors="ignore")


class xinwenUrlSearch(object):

    def __init__(self, city):
        self.spider_status = 0
        self.mysql_list_queue = 'xinwen.mysql.com:' + city
        self.list_queue = 'news.urls:' + city

    def url_to_queue(self, url_info):
        logger.info('insert data success: %s', url_info['remark']['website_name'])
        cache.lpush(self.list_queue, url_info)

    def get_paging(self,split_str,url_info):
        start = 0
        end = 0 
        count = 0 
        try:
            try:
                url = split_str.split(',')[0]
                start = int(split_str.split(',')[1])
                end = int(split_str.split(',')[2])
            except Exception:
                url_info['url'] = split_str
                self.url_to_queue(url_info)
                return
            for i in range(end):
                #分页只采集一遍，循环采集分页前两页
                if self.spider_status:
                    count += 1
                    if count > 2:
                        break
                step = ''
                try:
                    step = int(split_str.split(',')[3])
                except Exception:
                    pass
                if step:
                    url_info['url'] = url.replace('*', str((start+i)*step))
                else:
                    url_info['url'] = url.replace('*', str(i+start))
                self.url_to_queue(url_info)
        except Exception:
            logger.error("Exception:%s,split_str:%s", traceback.format_exc(),split_str)

    def get_paging_by_curl(self,split_str,url_info):
        start = 0
        end = 0
        count = 0
        try:
            try:
                url = split_str.split('!')[0]
                start = int(split_str.split('!')[1])
                end = int(split_str.split('!')[2])
            except Exception:
                url_info['url'] = split_str
                self.url_to_queue(url_info)
                return
            for i in range(end):
                #分页只采集一遍，循环采集分页前两页
                if self.spider_status:
                    count += 1
                    if count > 2:
                        break
                step = ''
                try:
                    step = int(split_str.split('!')[3])
                except Exception:
                    pass
                if step:
                    url_info['url'] = url.replace('@', str((start+i)*step))
                else:
                    url_info['url'] = url.replace('@', str(i+start))
                self.url_to_queue(url_info)
        except Exception:
            logger.error("Exception:%s,split_str:%s", traceback.format_exc(),split_str)

    def pages_url_to_queue(self, seed, city):
        try:
            url = seed.get('url')
            website_name = seed.get('name')
            website_domain = urlparse(url).netloc
            if website_domain:
                url_info = {"remark": {"city":city, "cookies":seed.get("cookies"),"url_reg_no_contains":seed.get('url_reg_no_contains'), "url_reg_contains":seed.get('url_reg_contains'), "website_name": website_name, "website_province": seed.get('province'), "website_city": seed.get('city'), "website_county": seed.get('county'), "record_id": seed.get('record_id'),
                                    "website_domain": website_domain, "website_url": url, "spider_depth": seed.get('depth'), "special_title_regex":seed.get('special_title_regex'), "special_title_xpath":seed.get('special_title_xpath'),
                                    "special_content_xpath":seed.get('special_content_xpath'),"special_time_regex":seed.get('special_time_regex'),"special_time_xpath":seed.get('special_time_xpath'),"special_author_xpath":seed.get('special_author_xpath'),"special_author_regex":seed.get('special_author_regex'), "license":seed.get('license')}
                    , "depth": 0, "retry_times": 0, "site_id": 1, "url": url}

                cache.lpush(self.mysql_list_queue, url_info)
                logger.info('insert data success: %s', website_name)
                """
                以下是列表页，所以设置采集深度为2
                """
                url_info['remark']['spider_depth'] = 2
                spider_status = seed.get('spider_status')
                #分页
                paging = seed.get('paging')#url,start,end;url,start,end;...
                if paging:
                    # 只采集一遍分页,重复采集分页前两页
                    if spider_status:
                        if int(spider_status)==1:
                            self.spider_status = 1
                        else:
                            self.spider_status = 0
                    #更新采集完分页的状态为1
                    mysqlUtil1.update_bus_mon_spider_site(website_name)
                    if paging.__contains__('curl'):
                        if paging.__contains__('>'):
                            urls = paging.split('>')
                            for split_str in urls:
                                split_str = split_str.replace('\\\n', '')# 去掉转义
                                split_str = split_str.replace('\\\\', '')
                                split_str = split_str.replace('\\', '')
                                self.get_paging_by_curl(split_str,url_info)
                        else:
                            url_regs = paging.replace('\\\n', '')# 去掉转义
                            split_str = url_regs.replace('\\\\', '')
                            url_regs = url_regs.replace('\\', '')
                            self.get_paging_by_curl(url_regs,url_info)
                    if paging.__contains__(';'):
                        urlsplit = ''
                        if '>' in paging:
                            urls = paging.split('>')
                            for i in urls:
                                if not 'curl' in i:
                                    urlsplit = i
                        if urlsplit:
                            urls = urlsplit.split(';')
                            for split_str in urls:
                                self.get_paging(split_str,url_info)
                        elif paging.__contains__('curl'):
                            pass
                        else:
                            urls = paging.split(';')
                            for split_str in urls:
                                self.get_paging(split_str,url_info)
                    if not ';' in paging and not '>' in paging:
                        self.get_paging(paging,url_info)
        except Exception:
            logger.error("Exception:%s,paging:%s", traceback.format_exc(),paging)

    def start(self, city):
        while True:
            try:
                if cache.llen(self.mysql_list_queue) > 1:
                    logger.info('xinwen.mysql.com>1:%s', city)
                    time.sleep(60)
                else:
                    list = mysqlUtil1.search_mysql_xinwen_list(city)
                    for seed in list:
                        self.pages_url_to_queue(seed, city)
            except Exception:
                logger.error("fetch_url exception:%s", traceback.format_exc())

if __name__ == '__main__':
    try:
        logger.info("parent progress pid:%s", os.getpid())
        city_list = str(crawl_config.get("city_list"))
        citys = []
        city_list = city_list.split(',')
        for i in city_list:
            citys.append(i)
        progress_list=[]
        for city in citys:
            logger.info("start xinwen crawl progress:%s", city)
            p = xinwenUrlSearch(city)
            p = Process(target=p.start, args=(city,))
            p.start()
            progress_list.append(p)
        logger.info("wait for all subprogress done")
        for po in progress_list:
            po.join()
        logger.info("all subprogress done")
    except Exception:
        logger.error("start exception:%s",traceback.format_exc())

