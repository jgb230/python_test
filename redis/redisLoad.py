#!/usr/bin/env python3
# coding=utf-8

import redis
import sys
import os
import json
import time

#redis_config = {
#    'host':'r-bp1mivwwkhcntb9p51pd.redis.rds.aliyuncs.com',
#    'port':6379,
#    'password':'Galaxyeye01'
#}

redis_config = {
   'host':'172.16.0.23',
   'port':6379
}

rds = redis.Redis(**redis_config)#单机
def test(fp):
    line=fp.readline()
    while line:
        js = eval(line)
        tp = js["type"]
        tl = js["ttl"]
        vl = js["value"]
        key = js["key"]
        pipe = rds.pipeline(transaction=True)
        pipe.delete(key)
        if tp == 'string':
            pipe.set(key, vl)
        elif tp == 'set':
            for v in vl:
                pipe.sadd(key, v)
        elif tp == 'list':
            for v in vl:
                pipe.lpush(key, v)
        elif tp == 'hash':
            pipe.hmset(key, vl)
        elif tp == 'zset':
            for v,c in vl:
                mp = {v:c,}
                pipe.zadd(key, mp)
        if tl > 0:
            tm = tl - int(time.time())
            if tm > 0:
                pipe.expire(key, tm)
        pipe.execute()
        line=fp.readline()
if __name__=="__main__":
    if not sys.argv[1:]:
        print("No filename input")
        sys.exit(1)
    try:
        fp = open(sys.argv[1],"r")
    except IOError as msg:
        sys.exit(msg)
    test(fp)
    
