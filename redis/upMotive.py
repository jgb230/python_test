#!/usr/bin/env python3
# coding=utf-8

""" 动机修改

Usage:
    upMotive [-ase] <element> <dim> <value> <robot>

Options:
    -h,--help  显示帮助菜单
    -a         增加
    -s         减少
    -e         等于

Example:
    苹果渴望增加20:
    upMotive -a 苹果 渴望 20 1803281346357cc6f33d1d79RI000020
    上动物学动机减少20:
    upMotive -s 上动物学 动机 20 1803281346357cc6f33d1d79RI000020
    美容喜好赋值20:
    upMotive -e 美容 喜好 20 1803281346357cc6f33d1d79RI000020
"""

import pymysql
import redis
from rediscluster import StrictRedisCluster
import configparser
import sys
import os
from docopt import docopt

db_config = {
    'host':'172.16.0.11',
    'port':3306,
    'user':'root',
    'passwd':'12345678',
    'db':'tesdb001',
    'charset':'utf8'
}
redis_config = {
    'host':'172.16.0.11',
    'port':7000
}

selectE = "select id from tb_element where description=%s"

db = pymysql.connect(**db_config)
rds = redis.Redis(**redis_config)#单机

print(os.system('source ~/tes/.bashrc'))

def parseConfig(file):
    global db_config
    global redis_config
    global db
    global rds
    cf = configparser.ConfigParser()
    cf.read(file)
    db_config['host'] = cf.get('DBMySql','ip')
    db_config['port'] = int(cf.get('DBMySql','port'))
    db_config['user'] = cf.get('DBMySql','user')
    db_config['passwd'] = cf.get('DBMySql','passwd')
    db_config['db'] = cf.get('DBMySql','dbname')
    db_config['charset'] = 'utf8'
    db = pymysql.connect(**db_config)

    clu = cf.get('Redis','is_cluster')
    if clu=='1':
        redis_config['host'] = cf.get('Redis','ip')
        redis_config['port'] = int(cf.get('Redis','port'))
        rds = redis.Redis(**redis_config)#单机
    elif clu=='2':
        redis_config['host'] = cf.get('Redis','addr').split(':')[0]
        redis_config['port'] = int(cf.get('Redis','addr').split(':')[1])
        rds = StrictRedisCluster(**redis_config)#集群


def getMIdVal(inlist):
    cursor = db.cursor()
    try:
        cursor.executemany(selectE, inlist)
        results = cursor.fetchall()
        for rw in results:
            yield rw
        cursor.close()
    except Exception as e:
        print(e)

def buildMkey(id,dim,robot):
    key = 'motive|'+str(id)+'|'+str(dim)+'|'+robot
    return key

def getRobotInfo():
    key='robot_info'
    try:
       mem = rds.smembers(key)
       for robot in mem:
           id = str(robot).split('|')[2]
           yield id
    except Exception as e:
        print(e)

def parseDim(dim):
    dimId = 0
    if dim=='渴望':
        dimId = 2
    elif dim=='动机':
        dimId = 1
    elif dim=='喜好':
        dimId = 3
    return dimId



if __name__=="__main__":

    args = docopt(__doc__)
    element = args['<element>']
    dim = args['<dim>']
    value = args['<value>']
    robot = args['<robot>']
    print(args)
    path = os.environ.get('MTSR_HOME')
    file = '/tes/config/TESConfig.ini'
    print(path+file)
    parseConfig(path+file)

    dimId = parseDim(dim)

    templist = [element]
    inlist = [templist]
    print(buildMkey(1,1,'1803281346357cc6f33d1d79RI000020'))
    id = 0
    for i in getMIdVal(inlist):
        id = i[0]
    print(id)
    key = buildMkey(id, dimId, robot)
    print(key)
    #for i in getRobotInfo():
        #print(i)
    
