# -*- coding: utf-8 -*-
# @Time    : 4/9/21 4:39 PM
# @Author  : wangjie
import init
import hashlib
import re
import json
import os
import random
import traceback
from urllib import parse
import requests
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
from multiprocessing import Process
from lxml import etree
from IdWorker import IdWorker
from worker.extractor.article_extractor import ArticleExtractor
from config import Config
from ulogger import setLogger
from worker.utils import tools
import solrUtil
from RedisClient import RedisClient
from worker.utils.headers import user_agent
log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"startCrawl")
crawl_config = Config().get_content("CRAWLER")
cache = RedisClient().conn

class xinwenSearch(object):

    def __init__(self, city):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        }
        self.requests_except = (
            requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError)
        self.http_proxy = crawl_config.get("useproxyip")
        self.proxy_api = crawl_config.get("proxyapi")
        self.maxRetryTime = 20
        self.seed_queue_priority = 0 #队列优先级
        self.seed_name = "searchName"
        self.quchong_queue = "xinwen:"
        self.proxy_ip = {}
        self.queue_max_fetch_count = 10 #队列最大消费次数
        self.queue_fetch_count = 0
        self.seed_queue_model = 'redis.xinwen.seedQueue.com:' + city
        self.seed_queue_error = "redis.xinwen.seedQueue.com0" #抓取异常种子放入低优先级
        self.data = {"pzr":"wj","title":"","body":"","license":"","county":"", "city":"","province":"","spidertype":"搜索", "channel":"", "country":"境内", "cat":"政府", "carrier":"新闻", "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
        # self.s = requests.session()
        self.IdWorker = IdWorker(1, 2, 0)

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

    def time_data(self, time_sj):                #传入单个时间比如'2019-8-01 00:00:00'，类型为str
        data_sj = time.strptime(time_sj,"%Y-%m-%d %H:%M:%S")       #定义格式
        time_int = int(time.mktime(data_sj))
        return time_int

    def millisecond_to_time(self, millis):
        """时间戳转换为日期格式字符串"""
        if len(str(millis)) == 13:
            millis = millis / 1000
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(millis))

    def extract_data(self, data):
        data = data.replace("</em>", "").replace("<em>", "")
        data = data.replace('\n', '')
        data = data.replace('\t', '')
        data = data.replace('\r', '')
        data = data.lstrip()
        data = data.rstrip()
        return data

    def escape_string(self, text):
        """
        只保留汉字
        """
        text = re.sub("<.*?>", "", text)
        text = re.sub("@([\s\S]*?):","",text)  # 去除@ ...：
        text = re.sub("\[([\S\s]*?)\]","",text)  # [...]：
        text = re.sub("@([\s\S]*?)","",text)  # 去除@... 
        text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+","",text)  # 去除标点及特殊符号
        text = re.sub("[^\u4e00-\u9fa5]","",text)  #  去除所有非汉字内容（英文数字）
        text = re.sub("客户端","",text)
        text = re.sub("回复","",text)
        return text

    def extract_detail(self, seed, html, url):
        try:
            if html:
                title=content=author=release_time=release_time_old=''
                article_extractor = ArticleExtractor(url, html)

                content_xpath = seed['remark']['special_content_xpath']
                title_regex = seed['remark']['special_title_regex']
                title_xpath = seed['remark']['special_title_xpath']
                author_xpath = seed['remark']['special_author_xpath']
                author_regex = seed['remark']['special_author_regex']
                time_regex = seed['remark']['special_time_regex']
                time_xpath = seed['remark']['special_time_xpath']

                content = article_extractor.get_content(content_xpath)
                title = article_extractor.get_title(title_regex,title_xpath)
                author = article_extractor.get_author(author_xpath, author_regex)
                release_time = article_extractor.get_release_time(time_regex, time_xpath)

                if 'mp.weixin.qq.com' in url:
                    search = re.search('",n=\"([0-9]*)\"', html)
                    if search:
                        timestamp = search.group(1)
                        postdate = self.millisecond_to_time(int(timestamp))
                        if postdate:
                            self.data["postdate"] = postdate
                    else:
                        self.data["postdate"] = self.data["updateTime"]
                    html = etree.HTML(html)
                    content = html.xpath('//div[@id="js_content"]')
                    if content:
                        content = content[0]
                        content = etree.tostring(content, encoding="utf-8").decode("utf-8")
                        content = tools.del_html_tag(content,save_img=True)

                if title and content:
                    if len(content)>10000:
                        content = self.escape_string(content)
                        if len(content)>10000:
                            content = content[:5000]
                    self.data["site"] = seed['remark']['website_name']
                    self.data["title"] = self.extract_data(title)
                    self.data["url"] = url

                    website_province = seed['remark']['website_province']
                    if website_province:
                        self.data['province'] = website_province
                    website_city = seed['remark']['website_city']
                    if website_city:
                        self.data['city'] = website_city
                    website_county = seed['remark']['website_county']
                    if website_county:
                        self.data['county'] = website_county
                    license = seed['remark']['license']
                    if license:
                        self.data['license'] = license
                    record_id = seed['remark']['record_id']
                    if record_id:
                        self.data['record_id'] = record_id
                    if author:
                        author = self.extract_data(author)
                        if len(author)>100:
                            self.data["author"] = self.data["site"]
                        else:
                            self.data["author"] = author
                    else:
                        self.data['author'] = self.data['site']
                    if not release_time:
                        release_time = article_extractor.get_release_time_old()
                    if not release_time:
                        release_time = article_extractor.get_release_time_all()
                    if not release_time.startswith('2'):
                        release_time = article_extractor.get_release_time_old()
                    if not 'mp.weixin.qq.com' in url:
                        if release_time:#如果不是规则的日期格式
                            search = re.search('([1-9]+)', release_time)
                            if search:
                                re_search = re.search('(.*)-(.*)-(.*) (.*):(.*):(.*)', release_time)
                                groups = ()
                                try:
                                    groups = re_search.groups()
                                except Exception:
                                    pass
                                if len(groups) == 6:
                                    self.data["postdate"] = release_time
                    if not 'postdate' in self.data.keys():
                        self.data["postdate"] = self.data['updateTime']
                    elif int(self.data["postdate"].split('-')[0])>int(time.strftime("%Y")):
                        self.data["postdate"] = self.data['updateTime']
                    imgs = re.findall(' src=\"?(.*?)(\"|>|\\s+)', content)
                    if imgs:
                        for img in imgs:#拼接图片
                            img = img[0]
                            if not img.__contains__('http'):
                                replace_url = tools.get_full_url(url,img)
                                content = content.replace(img, replace_url)
                    self.data['body'] = content
                    self.data['mediaCategory'] = '1'
                    self.data['id'] = self.get_md5(url)
                    solrUtil.add(self.data['id'], self.data["record_id"],self.data["title"],self.data["author"],self.data["postdate"],self.data["url"],self.data["updateTime"],self.data["carrier"],self.data["site"],self.data["cat"],self.data["body"],
                                        "1", self.data["province"], self.data["city"], self.data["county"], self.data["license"])
                    logger.info("insert data success")
                    self.data = {"pzr":"wj","title":"","body":"","pv":"","uv":"","ip_count":"","todayPv":"","pvTotal":"","share_count":"","license":"","county":"", "city":"","province":"","spidertype":"搜索", "channel":"", "country":"境内", "cat":"政府", "carrier":"新闻", "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
                else:
                    logger.info("搜索结果为空:%s", url)
                    if html.__contains__('window.location.href'):
                        search = re.search("window.location.href=\\'(.*?)\\'",html)
                        if search:
                            url = search.group(1)
                            seed['url'] = url
                            self.send_back_to_queue(com_name=seed)
                    self.data = {"pzr":"wj","title":"","body":"","pv":"","uv":"","ip_count":"","todayPv":"","pvTotal":"","share_count":"","license":"","county":"", "city":"","province":"","spidertype":"搜索", "channel":"", "country":"境内", "cat":"政府", "carrier":"新闻", "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")}
            else:
                logger.info("页面异常,搜索词:%s", url)
        except Exception:
            logger.error("extract exception:%s",traceback.format_exc())
            self.send_back_to_queue(com_name=seed)
        return None

    def get_md5(self,val):
        """把目标数据进行哈希，用哈希值去重更快"""
        md5 = hashlib.md5()
        md5.update(val.encode('utf-8'))
        return md5.hexdigest()

    def send_back_to_queue(self, com_name):
        logger.info('seed back to queue')
        cache.lpush(self.seed_queue_error, json.dumps({self.seed_name : com_name}))

    def fetch_article_detail_by_url2(self, seed, url, uri, uri2):
        count = 0
        while True:  # 循环重试
            try:
                time.sleep(0.1 + 0.1 * random.randint(0, 10))
                logger.info("Visited otherxinwen search page:%s", url)
                if not self.proxy_ip:
                    self.proxy_ip = self.get_proxy(self.proxy_ip)
                self.headers['Host'] = uri2
                self.headers['Referer'] = uri
                self.headers['User-Agent'] = random.choice(list(user_agent))
                req = requests.get(url, headers=self.headers, timeout=10, proxies=self.proxy_ip,allow_redirects=False, verify=False)
                if req.status_code == 200:
                    count = 0
                    content_type = req.headers.get('Content-Type', '')
                    if 'text/html' not in content_type:
                        logger.error('not is html on URL: %s' % (url))
                        break
                    html = tools._get_html_from_response(req)
                    self.extract_detail(seed, html, url)
                    break
                elif req.status_code == 404:
                    logger.info("页面找不到%s,statusCode:%d", url,req.status_code)
                    self.proxy_ip = self.get_proxy({})
                    count = count + 1
                    if count > self.maxRetryTime:
                        logger.info("重试次数超限:%s", url)
                        self.send_back_to_queue(seed)
                        break
                else:
                    logger.info("unexpect statusCode:%d", req.status_code)
                    self.send_back_to_queue(seed)
                    break
            except self.requests_except as e:
                logger.info("proxy invalid exception:%s", e)
                self.proxy_ip = self.get_proxy({})
                count = count + 1
                if count > self.maxRetryTime:
                    logger.info("重试次数超限:%s", url)
                    self.send_back_to_queue(seed)
                    break
            except Exception:
                logger.error("request exception:%s", traceback.format_exc())
                time.sleep(2)
                count = count + 1
                if count > self.maxRetryTime:
                    logger.info("重试次数超限:%s", url)
                    self.send_back_to_queue(seed)
                    break

    def fetch_article_detail_by_url(self, seed, url, uri, uri2):
        count = 0
        redirected_url = url
        while True:  # 循环重试
            try:
                time.sleep(0.1 + 0.1 * random.randint(0, 10))
                logger.info("Visited otherxinwen search page:%s", url)
                if not self.proxy_ip:
                    self.proxy_ip = self.get_proxy(self.proxy_ip)
                self.headers['Host'] = uri2
                self.headers['User-Agent'] = random.choice(list(user_agent))
                if url.__contains__('mp.weixin.qq.com'):
                    req = requests.get(url, headers=self.headers, timeout=5, proxies=self.proxy_ip, verify=False)
                else:
                    cookies = seed['remark']['cookies']
                    if cookies:
                        self.headers['Cookie']=cookies
                    req = requests.get(url, headers=self.headers, timeout=10, proxies=self.proxy_ip, allow_redirects=False, verify=False)
                redirected_url = req.url
                if req.status_code == 200:
                    content_type = req.headers.get('Content-Type', '')
                    proxy = req.headers.get('Server', '')
                    if 'Proxy' in proxy:
                        self.proxy_ip = self.get_proxy({})
                        count = count + 1
                        if count > self.maxRetryTime:
                            logger.info("重试次数超限:%s", url)
                            self.send_back_to_queue(seed)
                            break
                    elif 'text/html' not in content_type:
                        logger.error('not is html on URL: %s' % (url))
                        self.fetch_article_detail_by_url2(seed, url, uri, uri2)
                    else:
                        count = 0
                        html = tools._get_html_from_response(req)
                        self.extract_detail(seed, html, url)
                    if 'Cookie' in self.headers.keys():
                        self.headers.pop('Cookie')
                    break
                elif req.status_code == 404:
                    logger.info("页面找不到:%s", url)
                    self.proxy_ip = self.get_proxy({})
                    count = count + 1
                    if count > self.maxRetryTime:
                        logger.info("重试次数超限:%s", url)
                        self.send_back_to_queue(seed)
                        break
                elif req.status_code == 503:
                    self.send_back_to_queue(seed)
                    break
                elif not parse.unquote(redirected_url) == parse.unquote(url):
                    seed['url'] = redirected_url
                    self.send_back_to_queue(seed)
                    break
                else:
                    logger.info("unexpect statusCode:%d, url:%s", req.status_code, url)
                    break
            except self.requests_except as e:
                logger.info("proxy invalid exception:%s", e)
                self.proxy_ip = self.get_proxy({})
                count = count + 1
                if count > self.maxRetryTime:
                    logger.info("重试次数超限:%s", url)
                    self.send_back_to_queue(seed)
                    break
            except Exception:
                logger.error("request exception:%s", traceback.format_exc())
                time.sleep(2)
                count = count + 1
                if count > self.maxRetryTime:
                    logger.info("重试次数超限:%s", url)
                    self.send_back_to_queue(seed)
                    break

    def fetch_error_seed_from_queueList(self):
        queue = "{}".format(self.seed_queue_error)
        seed_ob_str = cache.rpop(queue)
        if seed_ob_str:  # 队列有数据
            com_obj = re.search("\"searchName\": \"([^\"]+)", seed_ob_str)
            if com_obj:
                seed = com_obj.group(1)
                return seed.encode('utf-8').decode('unicode_escape')

    def fetch_seed_from_queueList(self):
        while True:
            try:
                queue = "{}".format(self.seed_queue_model)
                seed_ob_str = cache.rpop(queue)
                if seed_ob_str:  # 队列有数据
                    return seed_ob_str
                else:
                    logger.info('all searchword done')
                    time.sleep(60)
            except Exception:
                logger.error("fetch_seed_from_queueList exception:%s", traceback.format_exc())
                time.sleep(60)

    def start_crawl(self):
        while True:
            try:
                seed = self.fetch_seed_from_queueList()
                if seed:
                    seed = eval(seed)
                    url = seed['url']
                    _parse = parse.urlparse(url)
                    domain = _parse.netloc
                    scheme = _parse.scheme
                    uri = scheme + '://' + domain
                    self.fetch_article_detail_by_url(seed, url, uri, domain)
            except Exception:
                logger.error("fetch_seed_from_queueList exception:%s", traceback.format_exc())
                time.sleep(60)

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
            p = xinwenSearch(city)
            p = Process(target=p.start, args=(p,))
            p.start()
            progress_list.append(p)
        logger.info("wait for all subprogress done")
        for po in progress_list:
            po.join()
        logger.info("all subprogress done")
    except Exception:
        logger.error("start exception:%s",traceback.format_exc())
