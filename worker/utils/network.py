# -*- coding: utf-8 -*-
'''
Created on 2017-12-06 10:13
---------
@summary:
---------
@author: Boris
'''
import os
current_dir = os.path.abspath(os.path.dirname(__file__))
rootpath = os.path.dirname(current_dir)
import json
import sys
import time


import requests
import worker.base.constance as Constance
import random
import configparser #读配置文件的
import codecs
from config import Config
from ulogger import setLogger
crawl_config = Config().get_content("CRAWLER")
log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"ArticleExtractor")

def get_conf_value(config_file, section, key):
    cp = configparser.ConfigParser(allow_no_value = True)
    with codecs.open(config_file, 'r', encoding='utf-8') as f:
        cp.read_file(f)
    return cp.get(section, key)
    
IPPROXY_ADDRESS = get_conf_value(rootpath + '/config.conf', 'ipproxy', 'address')

class NetWork():
    def __init__(self):
        self.browser_user_agent = self.get_user_agent()
        self.http_proxy = crawl_config.get("useproxyip")
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        }
        self.proxy_ip = {}
        self.request_timeout = 7
        self.proxy_api = crawl_config.get("proxyapi")
        self.proxies = self.get_proxy(self.proxy_ip)

    def get_proxy(self, proxy_ip):
        """
        获取代理
        """
        if self.http_proxy == "true": #使用ip
            if proxy_ip == {}:  #未设置ip
                retry_time = 0
                while True:
                    try:
                        req = requests.get(self.proxy_api)
                        ip_json_str = req.content.decode("utf-8")
                        logger.info("proxy api returned:%s", ip_json_str)
                        if ip_json_str == None or ip_json_str == "null":
                            logger.error("ip获取异常")
                            time.sleep(2)
                            retry_time = retry_time + 1
                            if retry_time == 3:
                                return {}
                            continue
                        ip_json_str = json.loads(ip_json_str, strict=False)
                        ip_json_str = ip_json_str.get("data")[0]
                        ip = ip_json_str.get('ip')
                        port = ip_json_str.get('port')
                    except:
                        logger.error("ip获取异常")
                        time.sleep(2)
                        retry_time = retry_time + 1
                        if retry_time == 3:
                            return {}
                        continue
                    proxies = {
                        'http': 'http://'+ip+':'+str(port),
                        'https': 'https://'+ip+':'+str(port)
                    }
                    return proxies
            else:#已设置ip
                return proxy_ip
        else: #不使用ip
            return {}


    def get_user_agent(self):
        try:
            return random.choice(Constance.USER_AGENTS)
        except:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"

if __name__ == '__main__':
    network = NetWork()
    print(network.browser_user_agent)
    print(network.proxies)