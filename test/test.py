
#!/usr/bin/python3
# coding=utf-8

import requests,json
import pymysql

g_host='172.16.0.17'
g_port=3306
g_user='root'
g_passwd='root'
g_db='tesdb001'
g_charset='utf8'

db = pymysql.connect(host=g_host, port=g_port, user=g_user, passwd=g_passwd, db=g_db, charset=g_charset)

class manager:
    def __init__(self):
        self.userList = []
        self.sgwDic = {"sgw":"SGW00001"}
        

    def printManager(self):
        for v in self.userList:
            print("name:%s,phone:%s,msg:%s"%(v.get("name"),v.get("phone"),v.get("msg")))
        print("sgwDic:%s %s %s"%(self.sgwDic.get("sgwurl"),self.sgwDic.get("sgwaccount"),self.sgwDic.get("sgwpwd")))

    def getSgw(self):
        cursor = db.cursor()
        gsql = "SELECT sgw_url,sgw_appid,sgw_appkey FROM sharedata.tb_smsgateway WHERE sgw_uuid='"+self.sgwDic.get("sgw")+"';"
        cont = ""
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                self.sgwDic["sgwurl"]=rw[0]
                self.sgwDic["sgwaccount"]=rw[1]
                self.sgwDic["sgwpwd"]=rw[2]
                break
            cursor.close()
        except:
            print("SELECT tb_smsgateway error")

    def getManager(self):
        cursor = db.cursor()
        gsql = "SELECT mi_name,mi_phone,ifnull(mi_msg,concat(\"有电话拨出,现在是\",now())) mi_msg FROM tesdb001.tb_manager_info;"
        cont = ""
        try:
            cursor.execute(gsql)
            results = cursor.fetchall()
            for rw in results:
                userdic = {}
                userdic["name"] = rw[0]
                userdic["phone"] = rw[1]
                userdic["msg"] = rw[2]
                self.userList.append(userdic)
            cursor.close()
        except:
            print("SELECT tb_manager_info error")

class myHttpClient:
    def __init__(self):
        self.manager = manager()

    def post(self, msgdic, encode):
        code = "application/x-www-form-urlencoded;charset=%s" %(encode)
        headers = {'content-type': code}
        res = requests.post(self.manager.sgwDic.get("sgwurl"), data = msgdic, headers = headers)
        print(res.text)

    def get(self, msgdic, encode):
        url = "%s?charset=%s&%s" %(self.manager.sgwDic.get("sgwurl"), encode, self.buildurl(msgdic))
        print("url:" + url)
        re = requests.get(url)
        print(re.text)

    def buildurl(self, dictMsg):
        msg = ""
        for key in dictMsg:
            msg = msg + "%s=%s&"%(key, dictMsg.get(key))
        msg=msg[0:-1]
        return msg

    def buildsmsMsg(self, phone, msg):
        dic = {}
        dic["account"] = self.manager.sgwDic.get("sgwaccount")
        dic["pswd"] = self.manager.sgwDic.get("sgwpwd")
        dic["mobile"] = phone
        dic["msg"] = msg
        dic["needstatus"] = "true"
        return dic

    def sendMsg(self, msg):
        self.manager.getSgw()
        self.manager.getManager()
        self.manager.printManager()
        for v in self.manager.userList:
            self.post(self.buildsmsMsg(v.get("phone"), ("%s,醒醒！,%s,%s")%(v.get("name"), v.get("msg"), msg)), "utf-8")
            #self.get(self.buildsmsMsg(phone, msg), "utf-8")

def main():
    hc = myHttpClient()
    hc.sendMsg( "python 测试")

if __name__ == '__main__':
    main()
