#!/usr/bin/env python3
# coding=utf-8
__author__ = 'Jianggb'
import requests
import json,sys,traceback
from PublicLogTool import logger

class httpClient():
    url = "http://127.0.0.1:5566"
    def __init__(self):
        pass

    def setIpPort(self, ipPort):
        "设置ip port"
        self.url = "http://" + ipPort

    def post(self, math:str, msgdic:dict):
        try:
            head = {"Content-Type":"application/json"}
            lmath = math.strip("/")
            lurl = f"{self.url}/{lmath}"
            logger.info(f"url:{lurl},reqs:{msgdic}")
            rp = requests.post(lurl, data=msgdic, headers=head)
            logger.info(f"resp:{rp.text}")
            return eval(rp.text)
        except Exception as e:
            traceback.print_exc()
            logger.info(f"error:{e}")
            return {"error":str(e)}

if __name__ == "__main__":
    hc = httpClient()
    hc.post("test", {"aaa":"aa"})