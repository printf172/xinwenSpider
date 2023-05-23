# -*- coding: utf-8 -*-
# @Time    : 5/19/21 9:17 AM
# @Author  : wangjie
import os

import pymysql
from dbutils.pooled_db import PooledDB
from requests import NullHandler


from config import Config
from ulogger import setLogger
log_path = str(os.path.dirname(os.path.abspath(__file__)))
logger=setLogger(log_path,"mysql")
mysql_config = Config().get_content("DATABASE2")
mysql_host = mysql_config.get("host")
mysql_port = mysql_config.get("port")
mysql_db = mysql_config.get("db_name")
mysql_user = mysql_config.get("user")
mysql_pwd = mysql_config.get("password")
dbchar = mysql_config.get("dbchar")

'''
连接池
'''
class MysqlPool(object):

    def __init__(self):
        self.POOL = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=1,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=1,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=1,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=1,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=2,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_pwd,
            database=mysql_db,
            charset=dbchar
        )
    def __new__(cls, *args, **kw):
        '''
        启用单例模式
        :param args:
        :param kw:
        :return:
        '''
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def connect(self):
        '''
        启动连接
        :return:
        '''
        conn = self.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self,conn, cursor):
        '''
        关闭连接
        :param conn:
        :param cursor:
        :return:
        '''
        cursor.close()
        conn.close()

    def fetch_all(self,sql, args):
        '''
        批量查询
        :param sql:
        :param args:
        :return:
        '''
        conn, cursor = self.connect()

        cursor.execute(sql, args)
        record_list = cursor.fetchall()
        self.connect_close(conn, cursor)

        return record_list

    def fetch_one(self,sql, args):
        '''
        查询单条数据
        :param sql:
        :param args:
        :return:
        '''
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.connect_close(conn, cursor)

        return result

    def insert(self,sql, args):
        '''
        插入数据
        :param sql:
        :param args:
        :return:
        '''
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row