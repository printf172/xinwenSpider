# -*- coding: utf-8 -*-
import os
import time
import pysolr
import traceback
import math

from ulogger import setLogger
from config import Config

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"solr")
crawl_config = Config().get_content("CRAWLER")

solr = pysolr.Solr(crawl_config.get("solr_url"), timeout=10)
maxRetryTime = 5
list = []

def date_to_time_stamp(time_sj):                #传入单个时间比如'2019-8-01 00:00:00'，类型为str
    try:
        """
        日期转为时间戳
        """
        date_sj = time.strptime(time_sj,"%Y-%m-%d %H:%M:%S")       #定义格式
        time_int = int(time.mktime(date_sj))
    except Exception:
        s = time.strftime("%Y-%m-%d %H:%M:%S")
        date_sj = time.strptime(s,"%Y-%m-%d %H:%M:%S")       #定义格式
        time_int = int(time.mktime(date_sj))
    return time_int

def millisecond_to_time(millis):
    """时间戳转换为日期格式字符串"""
    if len(str(millis)) == 13:
        millis = millis / 1000
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(millis))


def add(id, record_id,title,author,postdate,url,update,carrier,site,cat,body, media_category, province, city, county, license):
    try:
        data = {
                "id": id,
                "pzr": 'wj',
                "title": title,
                "body": body,
                "license": license,
                "county": county,
                "city": city,
                "province": province,
                "channel": site,
                "country": "境内",
                "cat": cat,
                "carrier": carrier,
                "update": millisecond_to_time((date_to_time_stamp(update)-28800)),
                "site": site,
                "url": url,
                "recordId": record_id,
                "author": author,
                "postdate": millisecond_to_time((date_to_time_stamp(postdate)-28800)),
                "mediaCategory": media_category,
            }
        list.append(data)
        if len(list)==10:
            try:
                solr.ping()
                if list:
                    solr.add(
                        list    
                    )
                    list.clear()
            except :
                logger.info("Error :%s", traceback.format_exc())
                for i in list:
                    solr.add(
                        i    
                    )
                    logger.info('循环写入成功')
                list.clear()
        else:
            return True
    except Exception:
        logger.error("Error: insert Exception:%s", traceback.format_exc())

def page_solr_data(q,page_no):
    try:  
        results = solr.search("%s" % q,**{"start":(int(page_no)-1)*10})
        number = results.hits
        page = int(math.ceil(number/10.0)) 
        page_content = {
            'pageContent': results,
            'page': page
        }
        return page_content
    except Exception:
        logger.error("Error: Search Exception:%s", traceback.format_exc())

def delete(id):
    try:
        solr.delete(id=id)
    except Exception:
        logger.error("Error: Delete Exception:%s", traceback.format_exc())

if __name__ == "__main__":
    # results = solr.add([
    #         {
    #             "id": '1111',
    #             "pzr": 'wj',
    #         }
    #     ])

    solr.delete(id='7cd7501c28c9d9c685eb3f9b5219e4b8')
    solr.commit()

