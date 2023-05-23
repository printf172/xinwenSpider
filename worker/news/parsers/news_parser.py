import json
from os import utime
import re
import sys
import os
from urllib.parse import urlparse


from worker.base import base_parser
import worker.news.parsers.base_parser as self_base_parser
import worker.utils.tools as tools
from worker.extractor.article_extractor import ArticleExtractor
from ulogger import setLogger

log_path = str(os.path.dirname(os.path.abspath(__file__)))
log=setLogger(log_path,"url_manager")
# print(article_extractor.article_extractor)
# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '新闻正文提取'
depthDict = {}
regex = r'<a.*?href.*?=.*?["|\'](.*?)["|\']'
# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    pass

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    pass
    # log.debug('''
    #     添加根url
    #     parser_params : %s
    #     '''%str(parser_params))

    # for task in parser_params:
    #     website_id = task[0]
    #     website_name = task[1]
    #     website_position = task[2]
    #     website_url = task[3]
    #     website_domain = tools.get_domain(website_url)
    #     spider_depth = task[4]

    #     base_parser.add_url(SITE_ID, website_url, remark = {'website_name':website_name, 'website_position':website_position, 'website_url':website_url, 'website_domain':website_domain, 'spider_depth':spider_depth})

#------------ 处理 begin ---------------
# @tools.log_function_time
def parser_url_info(url_info):
    log.info('处理 \n' + tools.dumps_json(url_info))
    root_url = url_info['url']
    depth = url_info['depth']
    remark = url_info['remark']
    website_name = remark['website_name']
    website_url = remark['website_url']
    website_domain =  remark['website_domain']
    spider_depth = remark['spider_depth']
    cookies = remark['cookies']

    return root_url, depth, remark, website_name, website_url, website_domain, spider_depth, cookies

# @tools.log_function_time
def get_html_url(website_url):
    html = tools.get_html(website_url)
    if not html:
        # base_parser.update_url('news_urls', root_url, Constance.EXCEPTION)
        return
    # 近一步取待做url
    urls = tools.get_urls(html)
    list = []
    for url in urls:
        url = tools.get_full_url(website_url, url)
        list.append(url)
    return list

# @tools.log_function_time
def add_html_url(root_url,html, depth, spider_depth, website_url, website_name, website_domain, remark):
    urls = []
    # 近一步取待做url
    if depth < spider_depth - 1:
        #如果类型等于list或者dict
        if isinstance(html, list):
            urls = tools.list_to_list(html)
            tools.clear_list()
        elif isinstance(html, dict):
            urls = tools.dict_to_list(html)
            tools.clear_list()
        else:
            urls = tools.get_urls(html,regex)
            urls += tools.get_urls(html,'"staticHref":"(.*?)",')
            urls += tools.get_urls(html,"window.open\('(.*?)'\)")
            urls += tools.get_urls(html,'<A.*?href.*?=.*?["|\'](.*?)["|\']')
        if len(urls)>1000:
            """
            一个网页最多的url数量
            """
            urls = urls[0:1000]
        for url in urls:
            if root_url.__contains__("curl"):
                url = tools.get_full_url(website_url, url)
            else:
                url = tools.get_full_url(root_url, url)
            if tools.is_domian(url,website_domain):
                base_parser.add_url(SITE_ID, url, depth + 1, remark = remark)
            elif 'mp.weixin.qq.com' in url:
                base_parser.add_url(SITE_ID, url, depth + 1, remark = remark)


# @tools.log_function_time
def parser_article(root_url, html, website_name, website_domain, website_position):
    content = title = release_time = author = ''
    article_extractor = ArticleExtractor(root_url, html)
    content = article_extractor.get_content()
    if content:
        title = article_extractor.get_title()
        release_time = article_extractor.get_release_time()
        author = article_extractor.get_author()
        uuid = tools.get_uuid(title, website_domain) if title != website_name else tools.get_uuid(root_url, ' ')

        log.info('''
            uuid         %s
            title        %s
            author       %s
            release_time %s
            website_name %s
            domain       %s
            position     %s
            url          %s
            content      %s
            '''%(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, '省略...'))

        if tools.is_have_chinese(content) and release_time and len(release_time) == 19:
            # 入库
            add_article(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, content)

# @tools.log_function_time
def add_article(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, content):
    self_base_parser.add_news_acticle(uuid, title, author, release_time, website_name, website_domain, website_position, root_url, content)

#------------- 处理end -----------------

# 必须定义 解析网址
# @tools.log_function_time
def parser(url_info):
    root_url, depth, remark, website_name, website_url, website_domain, spider_depth, cookies = parser_url_info(url_info)
    if root_url.__contains__('curl'):
        html = tools.get_html_by_curl(root_url)
    else:
        html = tools.get_html(root_url,cookies)
    if not html:
        # base_parser.update_url('news_urls', root_url, Constance.EXCEPTION)
        return
    # 近一步取待做url
    add_html_url(root_url,html, depth, spider_depth, website_url, website_name, website_domain, remark)

    # 解析网页
    # parser_article(root_url, html, website_name, website_domain, website_position)


def getUrlsDeep(url, depth = 2):
    try:
        u = depthDict[url]
        if(u>=depth):
            return

        #避免碰到了下载链接
        # if 'download' in str(url):
        #     return

        #获取此页中的所有连接
        clist = get_html_url(url)
        for c in clist:
            #判断深度字典有有无此键，达到去重目的
            if c not in depthDict:
                depthDict[c]=depthDict[url]+1
                getUrlsDeep(c)

    except Exception as e:
        pass


if __name__ == '__main__':
    url_info = {'remark': {'cookies':'','website_name': '法制网', 'website_position': 1, 'website_domain': 'www.tianshi.edu.cn', 'website_url': 'http://zltq.tl.nmgjjjc.gov.cn/category/yaowen.html?t=1631515696335', 'spider_depth': 5}, 'depth': 2, 'retry_times': 0, 'site_id': 1, 'url': 'http://zltq.tl.nmgjjjc.gov.cn/category/yaowen.html?t=1631515696335'}
    parser(url_info)