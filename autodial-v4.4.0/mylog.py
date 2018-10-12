# from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import logging

loglevel = logging.INFO
logfile = "./autodial.log"

# logHandler = RotatingFileHandler(logfile, mode='a', maxBytes=50*1024*1024, backupCount=10, encoding=None, delay=0)
logHandler = TimedRotatingFileHandler(logfile, when='D', interval=1, backupCount=20)
#logFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
logFormatter = logging.Formatter('%(asctime)s %(filename)-12s[line:%(lineno)d] %(thread)d %(levelname)s %(message)s')

logHandler.setFormatter(logFormatter)
logger = logging.getLogger('')
logger.addHandler(logHandler)
logger.setLevel(loglevel)
