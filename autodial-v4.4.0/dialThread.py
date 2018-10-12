import time
import datetime
import subprocess
import threading
import zmq,json

from mylog import logger
import calcProhibitedTime as cpTime
import myHttpClient as http

class dialThread:
    def __init__(self, dialTask, dbConn, prohibitSlot, brokerAddr):
        self.fslog = "/usr/local/freeswitch/log/freeswitch.log"
        self.dialTsk = dialTask
        self.dbConn = dbConn
        self.prohibitSlot = prohibitSlot
        self.calcPt = None
        self.dialGwIp = None
        self.gw_dict = {}
        self.dialQueue_dict = {}
        self.pausesecond = 0
        self.cacheRecords = {}
        self.cachecount = 10
        self.taskid = None
        self.dialExt = None
        self.brokerAddr = brokerAddr
        self.hc = http.myHttpClient(dbConn) #发送短信类

    def subprocessrun(self, cmd):
        ret = None
        try:
            cp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            logger.debug("call process result: %s", cp)
            if cp.returncode == 0:
                ret = cp.stdout.rstrip('\n')
        except:
            logger.error("Exception: execute %s", cmd)
        return ret

    def imsDial(self, gwLineName, rec):
        mobile = rec.get("cr_mobile")
        dialCmd = "fs_cli -x " + "'bgapi originate sofia/gateway/" + gwLineName + "/" + \
                   mobile + " " + self.dialExt + " XML public'"
        logger.info("imsDial cmd: %s", dialCmd)

        result = self.subprocessrun(dialCmd)
        rec['cr_status'] = 2
        rec['cr_calltime'] = datetime.datetime.now()
        self.dbConn.updateDialTime(rec)

    def sipDial(self, gwLineName, rec):
        mobile = rec.get("cr_mobile")
        dialCmd = "fs_cli -x " + "'bgapi originate user/" + \
                mobile + " " + self.dialExt + " XML public'"
        logger.info("imsDial cmd: %s", dialCmd)

        result = self.subprocessrun(dialCmd)
        rec['cr_status'] = 2
        rec['cr_calltime'] = datetime.datetime.now()
        self.dbConn.updateDialTime(rec)

    def goipDial(self, gwLineName, rec):
        mobile = rec.get("cr_mobile")
        goipcmd = "fs_cli -x 'sofia_contact user/" + gwLineName + "'"
        goipout = self.subprocessrun(goipcmd)
        if goipout == None or goipout.find("error") != -1:
            return -1
        
        regexcmd = "fs_cli -x 'regex " + goipout + "|^sofia/internal/sip:(.*)(@.*)|%2'"
        regexout = self.subprocessrun(regexcmd)
        if goipout == None or goipout.find("error") != -1:
            return -1
        
        diallcmd = "fs_cli -x 'bgapi originate {ignore_early_media=true}sofia/internal/sip:" \
                    + mobile + regexout + " " + self.dialExt + " XML public'"
        result = self.subprocessrun(diallcmd)
        if goipout == None or goipout.find("error") != -1:
            return -1

        logger.info("goipDialcmd: %s", diallcmd)
        rec['cr_status'] = 2
        rec['cr_calltime'] = datetime.datetime.now()
        self.dbConn.updateDialTime(rec)

    def getChanneluuid(self, mobile):
        grepcmd = "grep \"New Channel.*%s\" %s|tail -n1 |awk '{print $1}'"\
                    %(mobile, self.fslog)
        logger.info("grepcmd: %s", grepcmd)
        result = self.subprocessrun(grepcmd)
        logger.info("grepcmd result: %s", result)
        return result

    def isChannelClose(self, uuid):
        grepcmd = "grep \"%s.*Close Channel.*\" %s|tail -n1 |awk '{print $1}'"\
                    %(uuid , self.fslog)
        logger.info("grepcmd: %s", grepcmd)
        result = self.subprocessrun(grepcmd)
        logger.info("grepcmd result: %s", result)
        if result == None or len(result) < 20:
            return False
        logger.info("Channel already closed: %s", uuid)
        return True

    def uuidKill(self, uuid):
        diallcmd = "fs_cli -x 'uuid_kill %s'"%(uuid)
        logger.info("diallcmd: %s", diallcmd)
        result = self.subprocessrun(diallcmd)
        logger.info("diallcmd result: %s", result)
        if result == None or result.find("-ERR") != -1:
            return -1
        return 0

    def isDialFailed(self, newRec, oldstate):
        calltime = newRec.get('cr_calltime')
        newstate = newRec.get('cr_status')

        if calltime is None:
            return True
        currtime = datetime.datetime.now()

        delta = (currtime - calltime).seconds

        if delta >= self.dialTsk.get('task_hangup') and newstate == oldstate:
            logger.warning("Dial failed for %s", newRec.get('cr_mobile'))
            uuid = self.getChanneluuid(newRec.get('cr_mobile'))
            if uuid !=None and len(uuid)>30 and not self.isChannelClose(uuid):
                self.uuidKill(uuid)
            return True
        return False

    def isDialExpired(self, rec):
        calltime = rec.get('cr_calltime')
        if calltime is None:
            return False
        currtime = datetime.datetime.now()
        delta = (currtime - calltime).seconds
        if delta >= 600:
            rec['cr_status'] = 12 #the call ended abnormal.
            logger.error("The Dial has lasted 600 seconds for %s" % (rec.get('cr_mobile')))
            return True
        return False
    
    def build602(self, phone):
        dic = {}
        dic["cmd"] = 602
        dic["uid"] = phone
        dic["playerID"] = 0
        dic["robotType"] = 1
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

    def build600(self, robotId, phone, service):
        dic = {}
        dic["cmd"] = 600
        dic["uid"] = phone
        dic["robotid"] = robotId
        dic["user_service"] = service
        msg = json.dumps(dic, ensure_ascii=False).encode('utf-8')
        return msg

    def searchVbContent(self, taskid):
        record = self.dbConn.selectVerbalContent(taskid)
        if record == None:
            logger.warning("no vb_content taskId:%s!",taskid)
        content = record.get('vb_content')
        return content

    def reportDailFailed(self, newest):
        context = zmq.Context()  
        socket = context.socket(zmq.DEALER)  
        socket.connect(self.brokerAddr) 
        phone = newest.get('cr_mobile')
        taskid = newest.get('cr_taskid')

        msg602 = self.build602(phone)
        logger.info("msg602 %s!",msg602.decode("utf-8"))
        socket.send(msg602)
        cmd = 0
        robotId = ""
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN) 
        socks = dict(poller.poll(1000))

        if socks.get(socket) == zmq.POLLIN:  
            message = socket.recv_multipart()  
            tmp = ""
            for row in message:
                tmp = tmp + row.decode("utf-8")
            data = json.loads(tmp)
            if 'cmd' in data:
                cmd = json.loads(tmp)['cmd']
                if cmd != 700:
                    logger.warning("602 recv cmd is not 700!")
                    return
            else:
                logger.warning("602 recv no cmd!")
                return
            if 'robotList' in data and 'robotID' in json.loads(tmp)['robotList'][0]:
                robotId = json.loads(tmp)['robotList'][0]['robotID']
            else:
                logger.warning("602 recv no robotList!")
                return

        if robotId == "":
            print("602 recv no cmd!")
            return
        msg = self.searchVbContent(taskid)
        msg = msg + "未接通"
        msg600 = self.build600(robotId, phone, msg)
        logger.info("msg600 %s!",msg600.decode("utf-8"))
        socket.send(msg600)

    def isDialing(self, rec):
        phone = rec.get('cr_mobile')
        newest = self.dbConn.selectPhoneStatus(phone)
        if newest != None and len(newest) > 0:
            return True
        else:
            return False

    def superviseDialQueue(self, gw, dialQueue):
        gwType = self.gw_dict.get(gw).get('gw_type')
        gwLineName = self.gw_dict.get(gw).get('gw_linename')
        # gwUsername = self.gw_dict.get(gw).get('gw_username')
        markDelete = []

        for i in range(len(dialQueue)):
            newest = self.dbConn.selectOneCallRecord(dialQueue[i].get('cr_uuid'))
            newState = newest.get('cr_status')
            logger.info("supervise loop: %d, newState: %d"%(i, newState))

            if newState == 1: #wait to dial.
                try:
                    self.hc.sendMsgOutTime(dialQueue[i].get('cr_mobile'), dialQueue[i].get('cr_taskid'))
                except Exception as e:
                    logger.error("Error: sendmsg error: %s."%(e))
                if self.isDialing(dialQueue[i]):
                    logger.warning(" %s is dialing by other task, set back to 0!",dialQueue[i].get('cr_mobile'))
                    dialQueue[i]['cr_status'] = 0
                    self.dbConn.updateDialTime(dialQueue[i])
                    markDelete.append(i)
                    continue
                if gwType.upper() == 'GOIP':    #goip line.
                    self.goipDial(gwLineName, dialQueue[i])
                elif gwType.upper() == 'IMS':  #ims line.
                    self.imsDial(gwLineName, dialQueue[i])
                elif gwType.upper() == 'SIP':  #sip line.
                    self.sipDial(gwLineName, dialQueue[i])
                if self.pausesecond > 0:
                    time.sleep(self.pausesecond)
            elif newState == 2: #dialing.
                oldstate = dialQueue[i].get('cr_status')
                if self.isDialFailed(newest, oldstate):
                    newest['cr_status'] = 11  #11: dial failed.
                    self.dbConn.updateDialFailedTime(newest)
                    markDelete.append(i)
                    self.reportDailFailed(newest)
                else:
                    continue
            elif newState == 3: #answered.
                if self.isDialExpired(dialQueue[i]):
                    self.dbConn.updateDialFailedTime(dialQueue[i])
                    markDelete.append(i)
            elif newState == 10: #10: hangup.
                markDelete.append(i)
            elif newState == 13: #13: hangup.
                markDelete.append(i)
            elif newState == 0:  #0: the state set backup to unalloc, it's an error.
                markDelete.append(i)
            else:
                continue

        if len(markDelete) > 0:
            length = len(markDelete) 
            for i in range(len(markDelete)):
                dialQueue.pop(markDelete[length - i - 1])
        maxcall = self.gw_dict.get(gw).get('gw_concurrency')

        if self.calcPt.isTimeSlotProhibit(self.prohibitSlot) == False:
            if len(dialQueue) < maxcall:
                need = maxcall - len(dialQueue)
                for i in range(need):
                    if len(self.cacheRecords) > 0:
                        dialQueue.append(self.cacheRecords.pop(0))
        else:
            logger.info("Currently it's dial prohibited time for task %s, don't append to dialQueue."% \
                         (self.dialTsk.get('task_id')))
            logger.info("Ths task's prohibitSlot is %s"%(self.prohibitSlot))
        
        return
    
    def superviseDialQueueDict(self):
        for (gw, dialQueue) in self.dialQueue_dict.items():
            logger.info("The dial gw: %s"%(gw))
            logger.info("The dialQueue, len %d, %s\n"%(len(dialQueue), dialQueue))
            self.superviseDialQueue(gw, dialQueue)
        return
    
    def selectCacheCallrecords(self, taskid):
        if self.dbConn.selectDialTaskStatus(taskid) == 1:
            recs = self.dbConn.selectCallRecordsToDial(taskid, self.cachecount)
            if len(recs) > 0:
                for i in range(len(recs)):
                    self.dbConn.updateCallrecordToAlloc(recs[i].get('cr_uuid'))
            return recs
        return None

    def initDialQueue(self):
        for (gw, gwAttr) in self.gw_dict.items():
            maxcall = gwAttr.get('gw_concurrency')
            for i in range(maxcall):
                if len(self.cacheRecords) > 0:
                    self.dialQueue_dict.get(gw).append(self.cacheRecords.pop(0))
        return

    def checkCallDialing(self):
        sum = 0
        for (gw, dialQueue) in self.dialQueue_dict.items():
            sum += len(dialQueue)
        return sum
    
    def calcTotalGwLines(self):
        sum = 0
        for gw in self.gw_dict.values():
            logger.debug("gw details: %s"%(gw))
            sum += gw.get('gw_concurrency')
        return sum
    
    def initCacheQueue(self):
        self.cacheRecords = self.selectCacheCallrecords(self.taskid)
        if len(self.cacheRecords) == 0:
            logger.warning("No call records to dial for task %s."%(self.taskid))
            return
        logger.info("size of cacheRecords of the task: %d"%(len(self.cacheRecords)))
        
        self.initDialQueue()

    def withdrawCacheQueue(self):
        for i in range(len(self.cacheRecords)):
            callRec = self.cacheRecords[i]
            self.dbConn.updateCallrecordToUnalloc(callRec.get('cr_uuid')) #state 0: 恢复为未分配。
        self.cacheRecords.clear()

    def run(self):
        logger.info("sch dialThread to handle %s" % self.dialTsk.get('task_id'))
        logger.info("The Dial Task details: %s", self.dialTsk)

        self.taskid = self.dialTsk.get('task_id')
        self.cachecount = self.dialTsk.get('task_cachecount')
        self.dialExt = self.dialTsk.get('task_dialext')
        gateways = self.dbConn.selectGatewayConfig(self.taskid)
        if gateways == None or len(gateways) == 0:
            logger.error("No available gateway configured")
            return

        for i in range(len(gateways)):
            gw = self.dbConn.getGatewayAttr(gateways[i].get('task_gateway'))
            if gw != None:
                self.gw_dict[gateways[i].get('task_gateway')] = gw
                dialQueue = []
                self.dialQueue_dict[gateways[i].get('task_gateway')] = dialQueue
        
        gwLines = self.calcTotalGwLines()
        if gwLines > self.cachecount:
            self.cachecount = gwLines

        logger.info("self.gw_dict of the task: %s"%(self.gw_dict))
        logger.info("self.dialQueue_dict of the task: %s"%(self.dialQueue_dict))
        logger.info("total gateway concurrent lines: %d"%(gwLines))

        self.initCacheQueue()
        self.calcPt = cpTime.calcProhibitedTime()
        newState = None

        while True:
            newState = self.dbConn.selectDialTaskById(self.taskid).get('task_status')
            
            if newState == 1:
                if len(self.cacheRecords) == 0 and self.checkCallDialing() == 0:
                    if self.calcPt.isTimeSlotProhibit(self.prohibitSlot):
                        logger.info("Currently it's dial prohibited time for task %s, don't initCacheQueue." \
                                    %(self.dialTsk.get('task_id')))
                        logger.info("Ths task's prohibitSlot is %s"%(self.prohibitSlot))
                    else:
                        self.initCacheQueue()
                        if len(self.cacheRecords) == 0 and self.checkCallDialing() == 0:
                            break
                        else:
                            self.superviseDialQueueDict()
                else:
                    self.superviseDialQueueDict()
            else:
                if len(self.cacheRecords) > 0: #1: 任务运行状态
                    self.withdrawCacheQueue()

                if self.checkCallDialing() > 0:
                    self.superviseDialQueueDict()
                else:
                    break

            logger.info("wait 5 seconds to supervise another round.")
            time.sleep(5) #sleep to 2 seconds to supervise again.

        if newState == 1: #1: 任务运行状态
            self.dbConn.updateTbTask(self.taskid, 10) #10, 完成。
            logger.info("set task %s to finished and exit dialThread." % (self.taskid))
        else:
            logger.info("task %s has been set to %d, exit dialThread." % (self.taskid, newState))
        return