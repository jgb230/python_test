#!/usr/bin/python3

import random
from mylog import logger
from dbAccess import *
from scheduleTask import *
import hashlib
# pymysqlpool setup manual:
# 1. sudo apt-get install python3-pip
# 2. sudo pip3 install pymysql
# 3. pymysqlpool安装, 先下载地址： https://github.com/0xE8551CCB/pymysqlpool
# 4. sudo python3 setup.py install
# refs: http://www.php.cn/python-tutorials-373371.html

g_poolSize = 20    #the tasks can support.
g_dialInterval=10  #scan dialtask interval, unit is seconds.

brokerAddr = "tcp://127.0.0.1:3130"
# brokerAddr = "tcp://172.16.0.17:3130"

dbConfig = {
    'pool_name': 'aicall',
    'host': '172.16.0.17',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'sharedata',
    'pool_resize_boundary': 10,
    'enable_auto_resize': True,
    # 'max_pool_size': 10
}

dbConfigAliYun = {
     'pool_name': 'aicall',
     'host': '0.0.0.0',
     'port': 4417,
     'user': 'root',
     'password': 'TELEPHONENO',
     'database': 'sharedata',
     'pool_resize_boundary': 10,
     'enable_auto_resize': True,
     'max_pool_size': 10
 }

if __name__=="__main__":
    dbConn = dbAccess(**dbConfig)
    schTsk = scheduleTask(dbConn, g_poolSize, g_dialInterval, brokerAddr)
    schTsk.mainTask()