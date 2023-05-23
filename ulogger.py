import os
import time
from logging.handlers import TimedRotatingFileHandler

import logging
from config import Config
crawl_config = Config().get_content("CRAWLER")
log_level = crawl_config.get('log_level')

class MutiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):

    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        TimedRotatingFileHandler.__init__(self, filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc, atTime=atTime)

    def computeRollover(self, currentTime):
        # 将时间取整
        t_str = time.strftime(self.suffix, time.localtime(currentTime))
        t = time.mktime(time.strptime(t_str, self.suffix))
        return TimedRotatingFileHandler.computeRollover(self, t)

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        # 修改内容--开始
        # 在多进程下，若发现dfn已经存在，则表示已经有其他进程将日志文件按时间切割了，只需重新打开新的日志文件，写入当前日志；
        # 若dfn不存在，则将当前日志文件重命名，并打开新的日志文件
        if not os.path.exists(dfn):
            try:
                self.rotate(self.baseFilename, dfn)
            except FileNotFoundError:
                # 这里会出异常：未找到日志文件，原因是其他进程对该日志文件重命名了，忽略即可，当前日志不会丢失
                pass
        # 修改内容--结束
        # 原内容如下：
        """
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        """

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


def setLogger(filePath,loggerType):

    if len(filePath) == 0:
        filePath = str(os.getcwd()) + "/log"
    else:
        filePath = os.path.join(filePath, "log")
    if os.path.exists(filePath) == False:
        os.makedirs(filePath)

    filename =loggerType+'.log-' + time.strftime('%Y%m%d',time.localtime(time.time()))
    fileFullPath=filePath+"/"+filename
    fmt_str = '%(asctime)s - %(levelname)s - process-%(process)d - %(filename)s[:%(lineno)d] - %(message)s'
    fileshandle = MutiProcessTimedRotatingFileHandler(fileFullPath, when='MIDNIGHT', interval=1, backupCount=0,encoding='utf8')
    fileshandle.suffix = "%Y%m%d_%H%M%S.log"
    fileshandle.setLevel(log_level)
    formatter = logging.Formatter(fmt_str)
    fileshandle.setFormatter(formatter)
    logger = logging.getLogger(loggerType)
    logger.setLevel(logging.INFO)
    logger.addHandler(fileshandle)
    return logger

if __name__ == '__main__':
    logger=setLogger("","readmongo")
    logger.info('1')
    logger.info('2')
    logger.info('3')