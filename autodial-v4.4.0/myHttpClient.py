import time
import requests
import zmq,json
from mylog import logger
import calcProhibitedTime as cpTime
import hashlib
import random

class adminInfo:
    def __init__(self, dbConn):
        self.dbConn = dbConn
        self.userList = []
        self.sgwDic = {"sgw":"SGW00002"}

    def printAdminInfo(self):
        for v in self.userList:
            logger.info("name:%s,phone:%s,msg:%s"%(v.get("name"),v.get("phone"),v.get("msg")))
        logger.info("sgwDic:%s %s %s"%(self.sgwDic.get("sgwurl"),self.sgwDic.get("sgwaccount"),\
                     self.sgwDic.get("sgwpwd")))

    def getSgw(self):
        if self.sgwDic.get("sgwurl") != None and self.sgwDic.get("sgwaccount") != None \
            and self.sgwDic.get("sgwpwd") != None:
            return 1
        record = self.dbConn.selectSgw(self.sgwDic.get("sgw"))
        if record == None:
	        return 0
        self.sgwDic["sgwurl"] = record.get("sgw_url")
        self.sgwDic["sgwaccount"] = record.get("sgw_appid")
        self.sgwDic["sgwpwd"] = record.get("sgw_appkey")
        return 1

    def getAdminInfo(self):
        if len(self.userList) != 0:
            return
        records = self.dbConn.selectManager()
        for v in records:
            userdic = {}
            userdic["name"] = v.get("mi_name")
            userdic["phone"] = v.get("mi_phone")
            userdic["msg"] = v.get("mi_msg")
            userdic["time"] = v.get("mi_time")
            userdic["lastSendTime"] = 0
            self.userList.append(userdic)

class myHttpClient:
    def __init__(self, dbConn):
        self.adminInfo = adminInfo(dbConn)
        self.cpt = cpTime.calcProhibitedTime()
        self.interval = 20

    def post(self, msgdic, encode, rand):
        code = "application/json;charset=%s" %(encode)
        headers = {'content-type': code}
        url = "%s?sdkappid=%s&random=%s"%(self.adminInfo.sgwDic.get("sgwurl"), \
                    self.adminInfo.sgwDic.get("sgwaccount"), rand)
        logger.info("url:" + url)
        json_str = json.dumps(msgdic)
        res = requests.post(url, data = json_str, headers = headers)
        logger.info(json.loads(res.text))

    def get(self, msgdic, encode):
        url = "%s?charset=%s&%s" %(self.adminInfo.sgwDic.get("sgwurl"), encode, self.buildurl(msgdic))
        logger.info("url:" + url)
        re = requests.get(url)
        logger.info(re.text)

    def buildurl(self, dictMsg):
        msg = ""
        for key in dictMsg:
            msg = msg + "%s=%s&"%(key, dictMsg.get(key))
        msg=msg[0:-1]
        return msg

    def buildTXsmsMsg(self, param, tpl_id, phone, rand):
        nowTime = (int)(time.time())
        data = "appkey=%s&random=%s&time=%s&mobile=%s"%(self.adminInfo.sgwDic.get("sgwpwd"), rand, nowTime, phone)
        logger.info("data:"+data)
        dicPhone = {}
        dicPhone["mobile"] = phone
        dicPhone["nationcode"] = "86"
        dic = {}
        dic["ext"] = ""
        dic["extend"] = ""
        dic["params"] = param
        dic["sig"] = hashlib.sha256(data.encode('utf-8')).hexdigest()
        dic["tel"] = dicPhone
        dic["time"] = nowTime
        dic["tpl_id"] = tpl_id
        logger.info(dic)
        return dic

    def sendMsgOutTime(self, phone, taskid):
        if self.adminInfo.getSgw() == 0:
	        return
        self.adminInfo.getAdminInfo()
        rand = (int)(random.random() * 1000000000)
        #self.adminInfo.printAdminInfo()
        for v in self.adminInfo.userList:
            #在提醒时间内，且与上次发送时间间隔超过self.interval 分钟 ，发送短信
            if not self.cpt.isTimeSlotProhibit(v.get("time")) and (v.get("lastSendTime") == 0 or \
                (time.time() - v.get("lastSendTime") >= self.interval*60)):
                v["lastSendTime"] = time.time()
                param = []
                param.append(v.get("name"))
                param.append(time.strftime("%H:%M:%S", time.localtime()))
                param.append(phone)
                param.append(taskid)
                self.post(self.buildTXsmsMsg(param, 182702, v.get("phone"), rand), "utf-8", rand)
            else:
                logger.info("sendMsg check false: inslot:%d lastSendTime:%d now:%d phone:%s"%\
                            (self.cpt.isTimeSlotProhibit(v.get("time")), v.get("lastSendTime"), \
                            time.time(), v.get("phone")))
    
    def sendMsgTimeOut(self, taskid):
        if self.adminInfo.getSgw() == 0:
	        return
        self.adminInfo.getAdminInfo()
        rand = (int)(random.random() * 1000000000)
        #self.adminInfo.printAdminInfo()
        for v in self.adminInfo.userList:
            param = []
            param.append(taskid)
            self.post(self.buildTXsmsMsg(param, 177364, v.get("phone"), rand), "utf-8", rand)
