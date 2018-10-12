
#!/usr/bin/python3
# coding=utf-8

import paramiko
import re
import time

import datetime


#设置主机列表
host_list=({'ip':'121.196.204.197', 'port':22, 'username':'root', 'password':'Galaxyeye01'},
           {'ip':'172.16.0.17', 'port':22, 'username':'galaxyeye', 'password':'1'})

class font:
    def __init__(self):
        self.mytm = mytime()

    def printHead(self, str):
        str = str.center(50)
        str = str.center(150, '#')
        self.printWBK(str)

    def printTitle(self, str):
        self.printWBL("  %s %s"%(str, self.mytm.nowYmdHMS()))

    def printInfo(self, str, isFormat=False):
        for line in str.split('\n'):
            if len(line) > 0:
                if isFormat:
                    row = ""
                    for file in line.split('\t'):
                        row = "%s%-20s"%(row, file)
                    self.printWG("    %s"%(row))
                else:
                    self.printWG("    %s"%(line))

    def printError(self, str):
        for line in str.split('\n'):
            if len(line) > 0:
                self.printWR("    %s"%(line))

    def printWR(self, str):
        print("\033[0;31;47m%-150s\033[0m"%(str))

    def printWG(self, str):
        print("\033[0;32;47m%-150s\033[0m"%(str))

    def printWY(self, str):
        print("\033[0;33;42m%-150s\033[0m"%(str))

    def printWBK(self, str):
        print("\033[0;30;42m%-150s\033[0m"%(str))

    def printWBL(self, str):
        print("\033[0;34;47m%-150s\033[0m"%(str))

    def printWP(self, str):
        print("\033[0;35;47m%-150s\033[0m"%(str))

class mytime:
    def nowYmd(self):
        now_time = datetime.datetime.now()
        return now_time.strftime('%Y%m%d')
    
    def yesYmd(self):
        now_time = datetime.datetime.now()
        yes_time = now_time + datetime.timedelta(days=-1)
        return yes_time.strftime('%Y%m%d')

    def nowYmdHMS(self):
        now_time = datetime.datetime.now()
        return now_time.strftime('%Y%m%d%H%M%S')

    def yesYmdHMS(self):
        now_time = datetime.datetime.now()
        yes_time = now_time + datetime.timedelta(days=-1)
        return yes_time.strftime('%Y%m%d%H%M%S')

    def tesYmd(self):
        
        return "20180717"

class client:
    def __init__(self):
        self.sshclient = None
        self.initSSH()
        self.fnt = font()

    def __del__(self):
        self.sshclient.close()

    def initSSH(self):
        self.sshclient = paramiko.SSHClient()
        # 设置为接受不在known_hosts 列表的主机可以进行ssh连接
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, host):
        self.sshclient.connect(hostname=host['ip'], port=host['port'], username=host['username'], password=host['password'], allow_agent=False,look_for_keys=False)

    def execcmd(self, cmd):
        stdin, stdout, stderr = self.sshclient.exec_command(cmd)
        str_out = stdout.read().decode()
        str_err = stderr.read().decode()
        
        if str_out != "":
            str_err = ""

        dic = {"str_out":str_out,
               "str_err":str_err}
        return dic

class HostInfo:
    def __init__(self, client):
        self.client = client
        self.fnt = font()

    def getHostInfo(self):
        self.getMemInfo()
        self.getCPUInfo()
        self.getDFInfo()
        self.getNETInfo()

    def getMemInfo(self):
        self.fnt.printTitle("MEM:")
        cmd = 'cat /proc/meminfo|grep "MemTotal\|MemFree"'
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        
        if str_err != "":
            self.fnt.printError(str_err)
            return
        str_total = re.search(r'MemTotal:(\s*)(\d+) kB', str_out).group(2)        
        str_free = re.search(r'MemFree:(\s*)(\d+) kB', str_out).group(2)
        use = round(float(str_free)/float(str_total), 2)
        
        self.fnt.printInfo('MemTotal: %sKB ,MemFree: %sKB, Use: %s'%(str_total, str_free, 1-use))

    def getCPUInfo(self):
        self.fnt.printTitle("CPU:")
        cmd = 'cat /proc/stat | grep "cpu "'
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
    
        if str_err != "":
            self.fnt.printError(str_err)
            return
        else:
            cpu_time_list = re.findall('\d+', str_out)
            cpu_idle1 = cpu_time_list[3]
            total_cpu_time1 = 0
            for t in cpu_time_list:
                total_cpu_time1 = total_cpu_time1 + int(t)
    
        time.sleep(2)
        
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']

        if str_err != "":
            self.fnt.printError(str_err)
            return
        else:
            cpu_time_list = re.findall('\d+', str_out)
            cpu_idle2 = cpu_time_list[3]
            total_cpu_time2 = 0
            for t in cpu_time_list:
                total_cpu_time2 = total_cpu_time2 + int(t)
    
        cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 2)
        self.fnt.printInfo('CPU use:' + str(cpu_usage))

    def getDFInfo(self):
        self.fnt.printTitle("DISK:")
        cmd = 'df -lm'
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        
        if str_err != "":
            self.fnt.printError(str_err)
            return
    
        self.fnt.printInfo(str_out)

    def getNETInfo(self):
        self.fnt.printTitle("NET:")
        cmd = 'cat /proc/net/dev'
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        
        if str_err != "":
            self.fnt.printError(str_err)
            return
        self.fnt.printInfo(str_out)

class process:
    def __init__(self, client):
        self.client = client
        self.processNames = ['smartivr','freeswitch','worker','Mtsr', 'apache-tomcat', 'autodial']
        self.fnt = font()

    def getPinfo(self):
        pall = ""
        for pro in self.processNames:
            pall = "%s\|%s"%(pall, pro)

        pinfo = self.getPid(pall[2:])
        phead = "%-5s|%-24s|%-10s|%-100s"%("PID", "STARTTIME", "ETIME", "ARGS")
        self.fnt.printTitle("PROCESS:")
        self.fnt.printInfo(phead)
        self.fnt.printInfo(pinfo)   

    def getPid(self, pName):
        cmd = 'ps -A -eo pid,lstart,etime,args|grep "%s"|grep -iv "grep\|tail\|vi\|kworker" \
                |awk \'{printf("%%5s",$1);printf "|"$2" "$3" "$4" "$5" "$6"|";printf("%%10s",$7);printf "|";for(i=8;i<=NF;i++){printf $i" "};printf "\\n"}\''%(pName)
        
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        
        if str_err != "":
            self.fnt.printError(str_err)
            return
        return str_out

class logInfo:
    def __init__(self, client):
        self.client = client
        self.fnt = font()
        self.mytm = mytime()

    def getAllLog(self, ip):
        self.getSmartWebError(ip)
        self.getAutodialError(ip)
        self.getTaskInfo(ip)
        self.getWorkerInfo(ip)

    def exist(self, file):
        cmd = 'if [ -x %s ];then echo -n 1;else echo -n 0;fi'%(file)
        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        
        if str_err != "":
            self.fnt.printError(str_err)
            return

        if str(str_out) == '0':
            return False
        elif str(str_out) == '1':
            return True

    def getSmartWebError(self, ip):
        logPath = {"121.196.204.197":['/root/fsInstall/smartWeb/apache-tomcat-8.5.30/logs/localhost.%s.log'\
                                        %(time.strftime("%Y-%m-%d", time.localtime()))]}

        if ip not in logPath:
            return

        self.fnt.printTitle("SmartWeb Error:")
        for path in  logPath[ip]:
            if not self.exist(path):
                continue
            self.fnt.printError("SmartWeb hash Error!")
            self.fnt.printInfo("Error log:%s"%(path))

    def getAutodialError(self, ip):
        logPath = {"121.196.204.197":['/root/autodial.log']}

        if ip not in logPath:
            return

        self.fnt.printTitle("Autodial Error:")
        for path in  logPath[ip]:
            if not self.exist(path):
                continue
            
            cmd = 'grep -i ERROR %s'%(path)
            dic = self.client.execcmd(cmd)
            str_out = dic['str_out']
            str_err = dic['str_err']

            if str_err != "":
                self.fnt.printError(str_err)
                continue
            
            if str_out == "":
                continue

            self.fnt.printError("Autodial hash Error!")
            self.fnt.printInfo("Error info:%s"%(str_out))

    def getWorkerInfo(self, ip):
        logPath = {"121.196.204.197":['~/tes/log/worker.I%s*'%(self.mytm.yesYmd())]}

        if ip not in logPath:
            return

        self.fnt.printTitle("Worker Info:")

        allfile = ""
        for path in  logPath[ip]:
            cmd = 'ls %s'%(path)
            dic = self.client.execcmd(cmd)
            allfile = dic['str_out']
            str_err = dic['str_err']

            if str_err != "" and allfile == "":
                self.fnt.printError(str_err)
                continue        

            self.fnt.printInfo(allfile)

            cmd = '''grep '耗时' %s |awk '{print $9, $0}'|awk -F"]" '{a=substr($1,2);if ((a-2000)>0) \
                    {print substr($1,2)" us "substr($3,4)}}'|sort -n|tail -n10'''%(path)

            dic = self.client.execcmd(cmd)
            str_out = dic['str_out']
            str_err = dic['str_err']

            if str_err != "":
                self.fnt.printError(str_err)
                continue
            
            if str_out == "":
                continue

            self.fnt.printInfo("TOP info:\n%s"%(str_out))

    def getTaskInfo(self, ip):
        mysqlinfo = {"121.196.204.197":{'user':'root', 'pwd':'TELEPHONENO', 'database':'sharedata'}}
        task = []
        if ip not in mysqlinfo:
            return
        user = mysqlinfo[ip]['user']
        pwd = mysqlinfo[ip]['pwd']
        database = mysqlinfo[ip]['database']

        cmd = '''mysql -u%s -p%s %s << EOF\nselect task_id from tb_task where task_status=1;\nEOF\n\
                '''%(user, pwd, database)

        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        if str_err != "" and str_out == "":
            self.fnt.printError(str_err)
            return

        for line in str_out.split('\n'):
            if "task_id" in line or len(line)<5:
                continue
            task.append(line)

        self.fnt.printTitle("Running TaskInfo:")
        self.fnt.printInfo(str(task))

        begin = "%s000000"%(self.mytm.yesYmd())
        end = "%s235959"%(self.mytm.yesYmd())

        cmd = '''mysql -u%s -p%s %s << EOF\n\
                 select cr_taskid,cr_userid,cr_status,count(1) \
                 from tb_callrecord where cr_calltime>'%s' and cr_calltime<'%s' \
                 group by cr_taskid,cr_userid,cr_status;;\nEOF\n\
                '''%(user, pwd, database, begin, end)

        dic = self.client.execcmd(cmd)
        str_out = dic['str_out']
        str_err = dic['str_err']
        if str_err != "" and str_out == "":
            self.fnt.printError(str_err)
            return
        self.fnt.printTitle("CallRecord info beging:%s end:%s"%(begin, end))
        self.fnt.printInfo(str(str_out), True)



def main():
    myclient = client()
    ci = HostInfo(myclient)
    pr = process(myclient)
    log = logInfo(myclient)
    fnt = font()
    for host in host_list:
        fnt.printHead(host["ip"])
        myclient.connect(host)
        ci.getHostInfo()
        pr.getPinfo()
        log.getAllLog(host["ip"])

if __name__ == "__main__":
    main()