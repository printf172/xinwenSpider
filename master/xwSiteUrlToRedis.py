# -*- coding: utf-8 -*-
# @Time    : 4/9/21 4:39 PM
# @Author  : wangjie
import init
import os
import time
import traceback
from multiprocessing import Process
import threading
from config import Config
from worker.news.parsers import news_parser
from RedisClient import RedisClient
from ulogger import setLogger
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
crawl_config = Config().get_content("CRAWLER")

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"xwSiteUrlToRedis")
cache = RedisClient().conn

class xwSiteUrlToRedis(object):

    def __init__(self, city):
        self.detail_queue = 'redis.xinwen.seedQueue.com:' + city
        self.list_queue = 'news.urls:' + city

    '''
        循环采集url
    '''
    def start_crawl(self):
        while True:
            try:
                if cache.llen(self.detail_queue)>10000:
                    logger.info('redis.xinwen.seedQueue.com count > 10000')
                    time.sleep(60)
                else:
                    seed = cache.lpop(self.list_queue)
                    if seed:
                        j = eval(seed)
                        url = j['url']
                        depth = j['depth']
                        remark = j['remark']
                        url_info = {"remark": remark,
                                    "depth": depth, "retry_times": 0, "site_id": 1, "url": url}
                        logger.info("current_thread:%s - Visited xinwen search page:%s",threading.current_thread().ident, url)
                        news_parser.parser(url_info)
                    else:
                        logger.info('%s采集完了，sleep60秒。。。',self.list_queue)
                        time.sleep(60)
            except Exception:
                logger.error("start exception:%s", traceback.format_exc())

    def start(self, p):
        try:
            logger.info("parent progress pid:%s", os.getpid())
            ruyile_progress_num = int(crawl_config.get("crawl_progressnum"))
            executor = ThreadPoolExecutor(max_workers=ruyile_progress_num)  # 定义线程池，设置最大线程数量
            thread_list = [] 
            for i in range(ruyile_progress_num):
                logger.info("start xinwen crawl progress:%s", i)
                thrd = executor.submit(p.start_crawl,)  # 将线程添加到线程池
                thread_list.append(thrd)
            logger.info("wait for all subprogress done")
            result_list = []
            for task in as_completed(thread_list):
                result_list.append(task.result())
            logger.info("all subprogress done")
        except Exception:
            logger.error("start exception:%s",traceback.format_exc())

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
            p = xwSiteUrlToRedis(city)
            p = Process(target=p.start,args=(p,))
            p.start()
            progress_list.append(p)
        logger.info("wait for all subprogress done")
        for po in progress_list:
            po.join()
        logger.info("all subprogress done")
    except Exception:
        logger.error("start exception:%s",traceback.format_exc())
