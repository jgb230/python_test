import time
from concurrent.futures import ThreadPoolExecutor
from mylog import logger
import calcProhibitedTime as cpTime
import dialThread as dt
from dialThread import *

class scheduleTask:
    def __init__(self, dbConn, poolSize, dialInterval, brokerAddr):
        self.dbConn = dbConn
        self.poolSize = poolSize
        self.dialInterval = dialInterval
        self.brokerAddr = brokerAddr
        self.hc = http.myHttpClient(dbConn)

    def handleTask(self, taskRec, prohibitSlot):
        dialthread = dt.dialThread(taskRec, self.dbConn, prohibitSlot, self.brokerAddr)
        dialthread.run()

    def isInQueuedTasks(self, task, queuedTasks):
        for temp in queuedTasks:
            logger.debug("queuedTask: %s, task: %s " % (temp.get('task_id'), task.get('task_id')))
            if temp.get('task_id') == task.get('task_id'):
                return True
        return False

    def isTaskTheaded(self, task, threadedTasks):
        ret = False
        for temp in threadedTasks:
            logger.debug("threadedTask: %s, task: %s " % (temp, task.get('task_id')))
            if temp.get('task_id') == task.get('task_id'):
                ret = True
        return ret

    def removeFinishedTasks(self, threadedTasks, queuedTasks):
        markDelete = []
        i = 0
        for temp in threadedTasks:
            if self.dbConn.selectDialTaskById(temp.get('task_id')).get('task_status') != 1:
                markDelete.append(i)
                logger.info("task %s removed from threadedTasks" % (temp.get('task_id')))
            i += 1

        if len(markDelete) > 0:
            length = len(markDelete) 
            for i in range(len(markDelete)):
                threadedTasks.pop(markDelete[length - i - 1])

        markDelete = []
        i = 0
        for temp in queuedTasks:
            if self.dbConn.selectDialTaskById(temp.get('task_id')).get('task_status') != 1:
                markDelete.append(i)
                logger.info("task %s removed from queuedTasks" % (temp.get('task_id')))
                break
            i += 1
        if len(markDelete) > 0:
            length = len(markDelete) 
            for i in range(len(markDelete)):
                queuedTasks.pop(markDelete[length - i - 1])
        return

    def mainTask(self):
        cpt = cpTime.calcProhibitedTime()
        executor = ThreadPoolExecutor()
        isFirst = True
        queuedTasks = []
        threadedTasks = []
        count = 0
        tasksInDb = self.dbConn.selectDialTask()

        while (True):
            if not isFirst:
                tasksInDb = self.dbConn.selectDialTask()
            else:
                isFirst = False

            logger.info("tasksInDb: %s", tasksInDb)
            logger.info("queuedTasks: %s", queuedTasks)
            logger.info("threadedTasks: %s", threadedTasks)

            for task in tasksInDb:
                if not self.isInQueuedTasks(task, queuedTasks):
                    queuedTasks.append(task)
                
                if not self.isTaskTheaded(task, threadedTasks):
                    taskRec = self.dbConn.selectDialTaskById(task.get('task_id'))
                    logger.debug("taskRec to thread: %s"%(taskRec))
                    if len(taskRec) == 0:
                        continue
                    prohibitSlot = taskRec.get('task_timegroup')
                    if cpt.isTimeSlotProhibit(prohibitSlot):
                        logger.info("Currently it's prohibited to dial for task %s, don't init dialThread."%\
                                    (task.get('task_id')))
                        logger.info("Ths task's prohibitSlot is %s"%(prohibitSlot))
                        continue
                    else:
                        logger.debug("to submit thread: %s"%(task.get('task_id')))
                        executor.submit(self.handleTask, taskRec, prohibitSlot)
                        threadedTasks.append(task)

            count = count + 1
            if count == 30:
                count = 0
                records = self.dbConn.selectLatestTime()
                for record in records:
                    taskid = record.get("task_id")
                    try:
                        logger.info("任务:%s,已经20分钟没有呼出成功了,先暂停了"%(taskid))
                        self.hc.sendMsgTimeOut(taskid)
                        self.dbConn.updateTbTask(taskid, 2)
                    except Exception as e:
                        logger.error("Error: sendmsg error: %s."%(e))

            logger.info("wait %s seconds to take new task. count:%d\n", self.dialInterval, count)
            self.removeFinishedTasks(threadedTasks, queuedTasks)
            time.sleep(self.dialInterval)
