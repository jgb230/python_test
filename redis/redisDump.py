#!/usr/bin/env python3
# coding=utf-8

import redis
import sys
import os
import json
import time

redis_config = {
    'host':'172.16.0.23',
    'port':7002
}

rds = redis.Redis(**redis_config)#单机
def test():
    kwargs = {}
    if not False:
        kwargs['separators'] = (',', ':')
    else:
        kwargs['indent'] = 2
        kwargs['sort_keys'] = True
    encoder = json.JSONEncoder(**kwargs)
    keys = rds.keys()
    for key in keys:
        dc = {}
        dc["key"] = key.decode('utf-8','ignore')
        tp = rds.type(key).decode('utf-8')
        dc["type"] = tp
        tl = rds.ttl(key)
        if tl == None:
            dc["ttl"] = -1
        else:
            dc["ttl"] = tl + int(time.time())
        vl = None
        if tp == 'string':
            res = rds.get(key).decode('utf-8')
            #print(res)
            vl = res
        elif tp == 'set':
            res = rds.smembers(key)
            #print(res)
            vl = [v.decode('utf-8','ignore') for v in res]
        elif tp == 'list':
            res = rds.lrange(key, 0, -1)
            #print(res)
            vl = [v.decode('utf-8','ignore') for v in res]
        elif tp == 'hash':
            vl = {}
            res = rds.hgetall(key)
            #print(res)
            for k in res:
                vl[k.decode('utf-8','ignore')] = res[k].decode('utf-8','ignore')
        elif tp == 'zset':
            vl = [(k.decode('utf-8','ignore'), score) for k, score in rds.zrange(key, 0, -1, withscores=True)]
        dc["value"] = vl
        print(dc)
if __name__=="__main__":
    test()
    
