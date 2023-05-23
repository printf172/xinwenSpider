# -*- coding: utf-8 -*-
# @Time    : 5/21/21 10:49 AM
# @Author  : wangjie
import os

from config import Config

crawl_config = Config().get_content("CRAWLER")
host=crawl_config.get("redis_host")
port=int(crawl_config.get("redis_port"))
password=crawl_config.get("redis_pwd")


import redis

class RedisClient(object):

    def __init__(self):
        self.pool = redis.ConnectionPool(host=host, port=port, password=password, max_connections=50)

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self.getConnection()
        return self._conn

    def getConnection(self):
        self._conn = redis.Redis(connection_pool = self.pool)
