#!/usr/bin/env python
# coding=utf-8

import zmq,json

broker = "tcp://172.16.5.11:3130"

def build602(phone):
        dic = {}
        dic["cmd"] = 602
        dic["uid"] = phone
        dic["playerID"] = 0
        dic["robotType"] = 1
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

def build600(robotId, phone, service):
        dic = {}
        dic["cmd"] = 600
        dic["uid"] = phone
        dic["robotid"] = robotId
        dic["user_service"] = service
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

def sendFailedMsg():
        print("sendFailedMsg!-----")
        context = zmq.Context()  
        socket = context.socket(zmq.DEALER)  
        socket.connect(broker) 
        phone = "18600227230"
        taskid = ""

        msg602 = build602(phone)
        print("msg602 %s!"%(msg602.decode("utf-8")))
        socket.send(msg602)
        cmd = 0
        robotId = ""
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN) 
        socks = dict(poller.poll(1000))

        ret = socks.get(socket)
        print("ret:%s"%(ret))
        if ret == zmq.POLLIN:  
            message = socket.recv_multipart()  
            print("message:%s"%(message))
            tmp = ""
            for row in message:
                tmp = tmp + row.decode("utf-8")
            data = json.loads(tmp)
            if 'cmd' in data:
                cmd = json.loads(tmp)['cmd']
                if cmd != 700:
                    print("602 recv cmd is not 700!")
                    return
            else:
                print("602 recv no cmd!")
                return
            if 'robotList' in data and 'robotID' in json.loads(tmp)['robotList'][0]:
                robotId = json.loads(tmp)['robotList'][0]['robotID']
            else:
                print("602 recv no robotList!")
                return

        #robotId = '180418105225a217ea9a0ecdRI000010'
        if robotId == "":
            print("602 recv no cmd!")
            return
        msg = "贷款呼叫系统"
        msg = msg

        msg600 = build600(robotId, phone, msg)
        print("msg600 %s!"%(msg600.decode("utf-8")))
        socket.send(msg600)

if __name__=="__main__":
        sendFailedMsg()