# -*- coding: utf-8 -*-
# @Time    : 11/23/20 7:54 PM
# @Author  : wangjie

import re
import traceback

import requests
from lxml import etree

PATTERN_URl = "<a.*href=\"(https?://.*?)[\"|\'].*"

#获取网页源代码，注意使用requests时访问https会有SSL验证，需要在get方法时关闭验证
def getHtml(url):
    res = requests.get(url,verify=False)
    text = res.text
    return text
#有时还是会有警告，可以采用以下方式禁用警告
#import urllib3
#urllib3.disable_warnings()

#获取指定页面中含有的url
def getPageUrl(url,html=None):
    if html == None:
        html = getHtml(url)
    uList = re.findall(PATTERN_URl, html)
    return uList

depthDict = {}

def getUrlsDeep(url,depth = 3):
    try:
        u = depthDict[url]
        if(u>=depth):
            return

        #避免碰到了下载链接
        # if 'download' in str(url):
        #     return

        #获取此页中的所有连接
        clist = getPageUrl(url)
        print("\t\t"*depthDict[url],"#%d:%s"%(depthDict[url],url))
        for c in clist:
            #判断深度字典有有无此键，达到去重目的
            if c not in depthDict:
                depthDict[c]=depthDict[url]+1
                getUrlsDeep(c)

    except Exception as e:
        print(traceback.format_exc())

if __name__ == '__main__':
    startUrl = 'http://www.zge.gov.cn/'
    #爬取页面设置有第0级
    depthDict[startUrl] = 0
    #一共爬取2级
    getUrlsDeep(startUrl,depth=3)

