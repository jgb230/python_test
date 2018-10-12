
import time
import datetime
from mylog import logger

class calcProhibitedTime:
    def inSlotCompare(self, now, begin, end):
        logger.debug("To compare now %s, begin %s, end %s"%(now, begin, end))
        res = None

        if begin <= end:
            if now >= begin and now <= end:
                res = True
            else:
                res = False
        else:
            if now >= begin or now <= end:
                res = True
            else:
                res = False

        logger.debug("The compare result is %s"%(res))
        return res
    
    def addZero(self, hm):
        if len(hm[0]) == 1: #小时为个位数，前面需要加0.
            hm[0] = '0' + hm[0]
        if len(hm[1]) == 1: #分钟为个位数，前面需要加0.
            hm[1] = '0' + hm[1]

    def stripSecond(self, time):
        strTime = None

        if len(time) == 3:
            time.pop(2)
            self.addZero(time)
            strTime = ':'.join(time)
            logger.debug("stripped second and time is %s"%(strTime))
        elif len(time) == 2:
            self.addZero(time)
            strTime = ':'.join(time)
            logger.debug("it just contain hour and mins, %s"%(strTime))
        else:
            logger.debug("the time format has error, %s"%(':'.join(time)))

        return strTime

    def isInSlot(self, slot, now):
        if len(slot) == 0:
            return False
        
        nowArr = now.split(':')

        begin = slot.split('-')[0]
        bstripped = begin.lstrip().lstrip('[')
        beginArr = bstripped.split(':')

        end = slot.split('-')[1]
        estripped = end.rstrip().rstrip(']')
        endArr = estripped.split(':')

        nowHS = self.stripSecond(nowArr)
        beginHS = self.stripSecond(beginArr)
        endHS = self.stripSecond(endArr)

        if nowHS == None or beginHS == None or endHS == None:
            logger.error("Invalid time format, prohibit to dial out.")
            return True

        return self.inSlotCompare(nowHS, beginHS, endHS)
    
    def getCurrTime(self):
        localtime = time.asctime(time.localtime(time.time()))
        hourMinSec = localtime.split(' ')[-2]
        logger.debug("Current time: %s", hourMinSec)
        return hourMinSec
    
    def isInSlots(self, slots, now):
        for slot in slots:
            if self.isInSlot(slot, now):
                return True
        return False
        
    def isTimeSlotProhibit(self, timeGroup):
        slots = timeGroup.split(';')
        logger.debug("Configured prohibit time slots: %s", slots)

        now = self.getCurrTime()
        if self.isInSlots(slots, now):
            return True
        else:
            return False