
#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Jianggb'
import sys,os
from time import gmtime
from PublicLogTool import logger
from publicTool import *
from datetime import datetime
from httpClient import httpClient
class knowquery:
    "mid查询类"
    def __init__(self, httpcli:httpClient):
        self.httpClient = httpcli

    def parseRet(self, retdic):
        "解析返回结果"
        try:
            if retdic["returncode"] == '0':
                ret = retdic["msg"]
                return ret
            else:
                return retdic
        except Exception as e:
            logger.error(e)
            return retdic

    def queryByLeaf(self, mids, spaceid):
        "叶子查询根结构及词义,外部调用接口"
        path = "queryByLeaf"
        retdic = self.httpClient.post(path, {"mids":mids, "spaceid":spaceid})
        return self.parseRet(retdic)

    def queryCur(self, uid):
        "查询好奇"
        path = "getCuriosityByUid"
        retdic = self.httpClient.post(path, {"uid":uid})
        return self.parseRet(retdic)

    def queryByMid(self, mid):
        "查询mid结构及词义,外部调用接口"
        path = "queryByMid"
        retdic = self.httpClient.post(path, {"mid":mid})
        return self.parseRet(retdic)

    def delMids(self, mids):
        "删除所有id"
        path = "delMids"
        retdic = self.httpClient.post(path, {"mids":mids})
        return self.parseRet(retdic)

if __name__ == '__main__':
    kn = knowquery()
    kn.queryByMid("0de40003176092f2f0")
