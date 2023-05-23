# -*- coding: utf-8 -*-
'''
Created on 2018-06-19 17:17
---------
@summary: url 管理器， 负责缓冲添加到数据库中的url， 由该manager统一添加。防止多线程同时访问数据库
---------
@author: Boris
'''
import hashlib,os
import threading
import traceback
import worker.utils.tools as tools
# from worker.db.redisdb import RedisDB
import collections
from RedisClient import RedisClient
import re
from config import Config
from ulogger import setLogger
crawl_config = Config().get_content("CRAWLER")

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"urlManager")

MAX_URL_COUNT = 10 # 缓存中最大url数

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst

class UrlManager(threading.Thread, Singleton):
    def __init__(self, table_url = 'urls'):
        if not hasattr(self,'_table_url'):
            super(UrlManager, self).__init__()
            self._thread_stop = False
            self._urls_deque = collections.deque()
            self._table_url = table_url
            self._table_url_dupefilter = self._table_url + '_dupefilter'
            self._table_url_end_depth_dupefilter = self._table_url + '_end_depth_dupefilter'
            self.cache = RedisClient().conn
            self.quchong_list_queue = crawl_config.get("quchong_list_queue")
            self.quchong_detail_queue = crawl_config.get("quchong_detail_queue")

    def run(self):
        while not self._thread_stop:
            try:
                self.__add_url_to_db()
            except Exception as e:
                logger.error(e)

            # log.debug('缓存url数量 %s'%len(self._urls_deque))
            tools.delay_time(1)

    def stop(self):
        self._thread_stop = True

    def put_urls(self, urls):
        urls = urls if isinstance(urls, list) else [urls]
        for url in urls:
            self._urls_deque.append(url)

        if self.get_urls_count() > MAX_URL_COUNT: # 超过最大缓存，总动调用
            self.__add_url_to_db()

    def get_urls_count(self):
        return len(self._urls_deque)

    def clear_url(self):
        '''
        @summary: 删除redis里的数据
        ---------
        ---------
        @result:
        '''

        self._db.clear(self._table_url)
        self._db.clear(self._table_url_dupefilter)

    def print_url(self, i):
        while self._urls_deque:
            url = self._urls_deque.popleft()
            print(i, '-->', url)

    def get_md5(self,val):
        """把目标数据进行哈希，用哈希值去重更快"""
        md5 = hashlib.md5()
        md5.update(val.encode('utf-8'))
        return md5.hexdigest()

    def send_to_queue(self, queue, url, expiration_time):
        self.cache.setex(queue + self.get_md5(url), '', expiration_time)

    def is_exit(self, queue, url):
        return self.cache.exists(queue + self.get_md5(url))

    def url_to_queue(self, url_str, url, url_reg_contains, url_reg_no_contains):
        try:
            if url_reg_contains and url_reg_no_contains:
                splits = url_reg_contains.split(';')
                for i in splits:
                    i = i.strip()
                    if re.search(i, url):
                        no_splits = url_reg_no_contains.split(';')
                        for j in no_splits:
                            if re.search(j, url):
                                logger.info('排除url:'+url)
                                return
                        self.cache.lpush(self.detail_queue, url_str)
                        logger.info('详情：insert data success:'+url)
                        break
            elif url_reg_contains:
                splits = url_reg_contains.split(';')
                for i in splits:
                    i = i.strip()
                    if re.search(i, url):
                        self.cache.lpush(self.detail_queue, url_str)
                        logger.info('详情：insert data success:'+url)
                        break
            elif url_reg_no_contains:
                splits = url_reg_no_contains.split(';')
                for i in splits:
                    i = i.strip()
                    if re.search(i, url):
                        logger.info('排除url:'+url)
                        return
                self.cache.lpush(self.detail_queue, url_str)
                logger.info('详情：insert data success:'+url)
            else:
                self.cache.lpush(self.detail_queue, url_str)
                logger.info('详情：insert data success:'+url)
        except Exception:
            logger.error('insert error:%s', traceback.format_exc())

    def __add_url_to_db(self):
        while self._urls_deque:
            try:
                url_str = self._urls_deque.popleft()
                city = url_str['remark']['city']
                remark = url_str['remark']
                url = url_str['url']
                url_reg_contains = remark['url_reg_contains']
                url_reg_no_contains = remark['url_reg_no_contains']
                self.detail_queue = 'redis.xinwen.seedQueue.com:' + city
                self.list_queue = 'news.urls:' + city
                depth = url_str.get('depth', 0)
                max_depth = url_str.get('remark',{}).get('spider_depth', 0)
                if depth == max_depth - 1:
                    '''
                    入详情队列
                    '''
                    url_ = tools.clean_url(url)
                    if url_:
                        url_str['url'] = url_
                        is_exit = self.is_exit(self.quchong_detail_queue, url_)
                        self.send_to_queue(self.quchong_detail_queue, url_,60*60*24*7)
                        if not is_exit:
                            self.url_to_queue(url_str, url_, url_reg_contains, url_reg_no_contains)
                        else:
                            logger.info('详情url 重复:%s', url_)
                else:
                    url_ = tools.clean_url(url)
                    if url_:
                        url_str['url'] = url_
                        is_exit = self.is_exit(self.quchong_detail_queue, url_)
                        self.send_to_queue(self.quchong_detail_queue, url_, 60*60*24*7)
                        if not is_exit:
                            """
                            入详情队列
                            """
                            self.url_to_queue(url_str, url_, url_reg_contains, url_reg_no_contains)
                        else:
                            logger.info('详情url 重复:%s', url_)
                    is_exit = self.is_exit(self.quchong_list_queue, url)
                    if not is_exit:
                        """
                        入列表队列
                        """
                        self.send_to_queue(self.quchong_list_queue, url, 60*60*1)
                        self.cache.lpush(self.list_queue, url_str)
                        logger.info('列表：insert data success')
                    else:
                        logger.info('列表url 重复:%s', url)
            except Exception:
                logger.error('insert error:%s', traceback.format_exc())


if __name__ == '__main__':
    url_manager = UrlManager('dsfdsafadsf')

    for i in range(100):
        url_manager.put_urls(i)

    for i in range(5):
        threading.Thread(target = url_manager.print_url, args = (i, )).start()
