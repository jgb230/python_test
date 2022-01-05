# from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import logging,inspect,os,sys
#日志设置

sfile = sys.argv[0]
bpos = sfile.rfind('/')+1
epos = sfile.rfind('.') if sfile.rfind('.')>0 else len(sfile)
logfile = sfile[bpos:epos] + ".log"
loglevel = logging.INFO
# logHandler = RotatingFileHandler(logfile, mode='a', maxBytes=50*1024*1024, backupCount=10, encoding=None, delay=0)
logHandler = TimedRotatingFileHandler(logfile, when='D', interval=1, backupCount=20)
#logFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
logFormatter = logging.Formatter('%(asctime)s %(filename)-12s[line:%(lineno)d] %(thread)d %(levelname)s %(message)s')

#创建StreamHandler对象
sh = logging.StreamHandler()
#StreamHandler对象自定义日志级别
sh.setLevel(logging.DEBUG)
#StreamHandler对象自定义日志格式
sh.setFormatter(logFormatter)

logHandler.setFormatter(logFormatter)
logger = logging.getLogger('Public')
logger.addHandler(logHandler)
logger.addHandler(sh)
logger.setLevel(loglevel)
