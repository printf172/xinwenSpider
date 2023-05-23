from pymysql import NULL
from MysqlPool import MysqlPool
import os
import traceback

import mysqlUtil
from config import Config
from ulogger import setLogger

log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"mysql")
db = MysqlPool()


def search_mysql_sd_web_list(name):
    sql = "select id, license from sd_web_list where name = '%s'"
    try:
        results = db.fetch_all(sql,(name))
        if results:
            return results
        else:
            return False
    except Exception :
        logger.error("Error: unable to fetch data from mysql. exception:%s", traceback.format_exc())

def update_mysql_sd_web_list(name):
    sql = """update sd_web_list set spiderState=2 where id = '%s' """
    try:
        db.insert(sql,(name))
    except Exception:
        # 如果发生错误则回滚
        logger.error("Error: insert xinwen Exception:%s", traceback.format_exc())

def update_bus_mon_spider_site(name):
    sql = """update bus_mon_spider_site set spider_status=1 where name = %s """
    try:
        db.insert(sql,(name))
    except Exception:
        # 如果发生错误则回滚
        logger.error("Error: insert xinwen Exception:%s", traceback.format_exc())

def search_mysql_xinwen_list(city):
    sql = "select * from bus_mon_spider_site where status = 2 and url != '' and is_deleted = 0 and city=%s ORDER BY update_time DESC"
    try:
        results = db.fetch_all(sql,(city))
        if results:
            return results
        else:
            return False
    except Exception :
        logger.error("Error: unable to fetch data from mysql.exception:%s", traceback.format_exc())

def search_mysql_first_xinwen_list(city):
    sql = "select * from bus_mon_spider_site where status = 2 and url != '' and is_deleted = 0 and list_page != '' and city=%s ORDER BY update_time DESC"
    try:
        results = db.fetch_all(sql,(city))
        if results:
            return results
        else:
            return False
    except Exception :
        logger.error("Error: unable to fetch data from mysql.exception:%s", traceback.format_exc())

def search_xinwen_list():
    sql = "select record_id, province, city, county, license, name from bus_mon_spider_site where province = 12"
    try:
        results = db.fetch_all(sql,())
        if results:
            return results
        else:
            return False
    except Exception :
        logger.error("Error: unable to fetch data from mysql.exception:%s", traceback.format_exc())

if __name__ == '__main__':
    xinwen_list = search_xinwen_list()
    for xinwen in xinwen_list:
        mysqlUtil.update_seed(xinwen[5],xinwen[0],xinwen[1],xinwen[2],xinwen[3],xinwen[4])
