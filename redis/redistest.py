#!/usr/bin/env python3
# coding=utf-8

import redis
import sys
import os
import json
import time
redis_config = {
    'host':'172.16.0.23',
    'port':7000
}

rds = redis.Redis(**redis_config)#单机
def test():
    print(int(time.time()))
if __name__=="__main__":
    test()
    
