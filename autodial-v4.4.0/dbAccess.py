import pymysql
from pymysqlpool import ConnectionPool
from mylog import logger

class dbAccess:
    def __init__(self, **dbConfig):
        self.pool = ConnectionPool(**dbConfig)

    def selectGatewayConfig(self, taskid):
        sql = "select DISTINCT task_gateway from tb_task WHERE task_id='%s'"%(taskid)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch gateway data.")
        logger.debug("selectGatewayConfig by taskid results: %s", records)
        return records
    
    def getGatewayAttr(self, gwId):
        sql = "select gw_uuid, gw_username, gw_linename, gw_type, gw_status, \
               gw_concurrency from tb_gateway WHERE gw_uuid='%s'and gw_status=True"%(gwId)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch gateway attributes.")
        if records != None and len(records) > 0:
            return records[0]
        else:
            return None

    def selectDialTask(self):
        sql = "select distinct task_id from tb_task WHERE task_status = 1"
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch dial task data.")

        return records
    
    def selectDialTaskById(self, taskid):
        sql = "select task_uuid, task_id, task_userid, task_username, task_status, \
               task_maxcall, task_pausesecond, task_cachecount, task_timegroup, \
               task_gatewaytype, task_gateway, task_dialext, task_hangup from tb_task \
               WHERE task_id = '%s'"%(taskid)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch dial task data.")
        logger.debug("selectDialTask by taskid results: %s", records)
        if records != None and len(records) > 0:
            return records[0]
        else:
            return None

    def selectDialTaskStatus(self, task_id):
        sql = "select task_status from tb_task WHERE task_id='%s'"%(task_id)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch dial task data.")
        if records != None and len(records) > 0:
            return records[0].get('task_status')
        else:
            return None

    def selectPhoneStatus(self, Phone):
        sql = "select cr_uuid, cr_taskid, cr_mobile, cr_status, cr_calltime \
               from tb_callrecord where cr_mobile='%s' and cr_status=2;"%(Phone)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch dial task data.")
        if records != None and len(records) > 0:
            return records
        else:
            return None

    def selectCallRecordsToDial(self, taskid, cacheNum):
        sql = "select cr_uuid, cr_taskid, cr_mobile, cr_status, cr_calltime from \
               tb_callrecord WHERE cr_taskid = '%s' and cr_status = 0 \
               order by cr_uuid limit %d"%(taskid, cacheNum)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch call records data.")

        return records

    def selectOneCallRecord(self, uuid):
        sql = "select cr_uuid, cr_taskid, cr_mobile, cr_status, cr_calltime from \
               tb_callrecord WHERE cr_uuid = %d"%(uuid)
        record = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                record = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch a call record data.")

        return record[0]
    
    def selectGw(self, uuid):
        sql = "select cr_uuid, cr_taskid, cr_mobile, cr_status, cr_calltime from \
               tb_callrecord WHERE cr_uuid = %d"%(uuid)
        record = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                record = cursor.fetchall()
                logger.debug(record)
            except:
                logger.error("Error: unable to fetch gw record data.")

        return record

    def updateDialTime(self, rec):
        state = rec.get('cr_status')
        uuid = rec.get('cr_uuid')
        sql = "UPDATE tb_callrecord SET cr_calltime=NOW(3), cr_status=%d WHERE cr_uuid=%d"%(state, uuid)
        logger.debug("updateDialTime sql: %s", sql)
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                logger.error("Error: unable to update dial time.")
        return
    
    def updateDialFailedTime(self, rec):
        state = rec.get('cr_status')
        uuid = rec.get('cr_uuid')
        sql = "UPDATE tb_callrecord SET cr_endtime=NOW(3), cr_status=%d WHERE cr_uuid=%d"%(state, uuid)
        logger.debug("updateDialFailedTime sql: %s", sql)

        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                logger.error("Error: unable to update failed call time data.")
        return
    
    def updateCallrecordToAlloc(self, uuid):
        sql = "update tb_callrecord set cr_status = 1 where cr_uuid=%d"%(uuid)
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                logger.error("Error: unable to update tb_callrecord to alloc.")
        return

    def updateCallrecordToUnalloc(self, uuid):
        sql = "update tb_callrecord set cr_status = 0 where cr_uuid=%d"%(uuid)
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
            except:
                logger.error("Error: unable to update tb_callrecord to unalloc.")
        return

    def selectAllTasksById(self, taskid):
        sql = "select task_uuid from tb_task WHERE task_id='%s'"%(taskid)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to selectAllTasksById by %s."%(taskid))
        return records

    def selectVerbalContent(self, taskid):
        sql = "select vb_content from tb_verbal where vb_uuid =\
               (select task_verbal from tb_task where task_id='%s')"%(taskid)
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except Exception as e:
                logger.error("Error: unable to selectVerbalContent by %s :%s."%(taskid, e))
        if records == None:
            return None
        else :
            return records[0]

    def selectSgw(self, uuid):
        sql = "SELECT sgw_url,sgw_appid,sgw_appkey FROM tb_smsgateway WHERE sgw_uuid='%s';"%(uuid)
        record = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                record = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch tb_smsgateway record data.")
        if record == None:
            return None
        else :
            return record[0]

    def selectManager(self):
        sql = "SELECT mi_name,mi_phone,now() \
               mi_msg,mi_time FROM tb_manager_info;"
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch tb_manager_info record data.")

        return records

    def selectLatestTime(self):
        sql = "SELECT task_id FROM tb_task WHERE task_status = 1 \
                and task_id not in (\
                SELECT distinct cr_taskid FROM tb_callrecord  WHERE cr_taskid in (SELECT task_id FROM tb_task WHERE task_status = 1)\
                AND cr_status = 10 AND cr_calltime < NOW(3) AND cr_calltime > DATE_SUB(NOW(3), INTERVAL 20 MINUTE))\
                and task_id in (\
                SELECT distinct cr_taskid FROM tb_callrecord b WHERE cr_taskid in (SELECT task_id FROM tb_task WHERE task_status = 1)\
                AND cr_calltime < DATE_SUB(NOW(3), INTERVAL 20 MINUTE) AND cr_calltime > DATE_SUB(NOW(3), INTERVAL 80 MINUTE));"
        records = None
        with self.pool.cursor() as cursor:
            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except:
                logger.error("Error: unable to fetch tb_task record data.")

        return records

    def updateTbTask(self, taskid, state):
        tasks = self.selectAllTasksById(taskid)
        if tasks == None or len(tasks) == 0:
            logger.warning("Warning, no task need to update status.")
            return
        
        for i in range(len(tasks)):
            sql = "UPDATE tb_task SET task_status=%s WHERE task_uuid='%d'"%(state, tasks[i].get('task_uuid'))
            with self.pool.cursor() as cursor:
                try:
                    cursor.execute(sql)
                except:
                    logger.error("Error: unable to update call task status.")
        return
