# -*- coding: utf-8 -*-
# @Time    : 5/21/21 5:02 PM
# @Author  : wangjie
import init
import os
import time
import traceback
from multiprocessing import Process


import redis

from worker.news.parsers import news_parser
from config import Config
from ulogger import setLogger


log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"main")
crawl_config = Config().get_content("CRAWLER")
cache = redis.Redis(host=crawl_config.get("redis_host"), port=int(crawl_config.get("redis_port")), password=crawl_config.get("redis_pwd"), decode_responses=True, errors="ignore")


class xinwenUrlSearch(object):

    def __init__(self, city):
        self.mysql_list_queue = 'xinwen.mysql.com:' + city
        self.list_queue = 'news.urls:' + city

    '''
        采集url到redis
    '''
    def start(self):
        while True:
            try:
                
                if cache.llen(self.list_queue) > 10000:
                    logger.info('正在采集：%s',self.list_queue)
                    time.sleep(10)
                else:
                    seed = cache.lpop(self.mysql_list_queue)
                    if seed:
                        seed = eval(seed)
                        logger.info('正在采集：%s', seed['remark']['website_name'])
                        news_parser.parser(seed)
                    else:
                        logger.info('empty')
                        time.sleep(10)
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
            logger.info("start xinwen crawl progress:%s", i)
            p = xinwenUrlSearch(city)
            p = Process(target=p.start,)
            p.start()
            progress_list.append(p)
        logger.info("wait for all subprogress done")
        for po in progress_list:
            po.join()
        logger.info("all subprogress done")
    except Exception:
        logger.error("start exception:%s",traceback.format_exc())
