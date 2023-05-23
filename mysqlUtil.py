from MysqlPool import MysqlPool
from pymysql.converters import escape_string
import os
import traceback

from config import Config
from ulogger import setLogger

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"mysql")
db = MysqlPool()

def insert_seed(record_id, ARTICLE_TITLE, ARTICLE_AUTHOR, PUBLISH_DATE, ARTICLE_URL, UPDATE_DATE, ARTICLE_CARRIER, WEB_NAME, WEB_SOURCE, ARTICLE_CONTENT, WEB_CHANNEL, media_category, province, city, county, license):
    sql = """insert into xinwen(record_id,ARTICLE_TITLE,ARTICLE_AUTHOR,PUBLISH_DATE,ARTICLE_URL,UPDATE_DATE,ARTICLE_CARRIER,WEB_NAME,WEB_SOURCE,ARTICLE_CONTENT,WEB_CHANNEL, media_category, province, city, county, license )values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
       db.insert(sql,(record_id, escape_string(ARTICLE_TITLE), ARTICLE_AUTHOR, PUBLISH_DATE, ARTICLE_URL, UPDATE_DATE, ARTICLE_CARRIER, WEB_NAME, WEB_SOURCE, escape_string(ARTICLE_CONTENT), WEB_CHANNEL, media_category, province, city, county, escape_string(license)))
    except Exception:
        # 如果发生错误则回滚
        logger.error("Error: insert Exception:%s", traceback.format_exc())


def insert_seed2(record_id, ARTICLE_TITLE, ARTICLE_AUTHOR, PUBLISH_DATE, ARTICLE_URL, UPDATE_DATE, ARTICLE_CARRIER, WEB_NAME, WEB_SOURCE, ARTICLE_CONTENT, WEB_CHANNEL, media_category, province, city, county, license, ipTotal,pvTotal,todayIp,todayPv,todayUv,uvTotal, views):
    sql = """insert into xinwen2(record_id, ARTICLE_TITLE, ARTICLE_AUTHOR, PUBLISH_DATE, ARTICLE_URL, UPDATE_DATE, ARTICLE_CARRIER, WEB_NAME, WEB_SOURCE, ARTICLE_CONTENT, WEB_CHANNEL, media_category, province, city, county, license, ipTotal,pvTotal,todayIp,todayPv,todayUv,uvTotal, views)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        db.insert(sql,(record_id, ARTICLE_TITLE, ARTICLE_AUTHOR, PUBLISH_DATE, ARTICLE_URL, UPDATE_DATE, ARTICLE_CARRIER, WEB_NAME, WEB_SOURCE, ARTICLE_CONTENT, WEB_CHANNEL, media_category, province, city, county, license, ipTotal,pvTotal,todayIp,todayPv,todayUv,uvTotal, views))
    except Exception:
        # 如果发生错误则回滚
        logger.error("Error: insert Exception:%s", traceback.format_exc())

def search_xinwen_list(name):
    sql = "select record_id from xinwen where WEB_NAME = '%s'"
    try:
        results = db.fetch_all(sql,(name))
        if results:
            return results
        else:
            return False
    except Exception :
        logger.error("Error: unable to fetch data from mysql.exception:%s", traceback.format_exc())

def update_seed(WEB_NAME, record_id, province, city, county, license):
    sql = """update xinwen set record_id='%s',province='%s',city='%s',county='%s',license='%s' where WEB_NAME = '%s';"""
    try:
        db.insert(sql,(WEB_NAME, record_id, province, city, county, license))
    except Exception:
        # 如果发生错误则回滚
        logger.error("Error: insert xinlangkandian Exception:%s", traceback.format_exc())
