import os
import sys
import logging
from threading import Timer

log = logging.getLogger('watchdog')
ch = logging.NullHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class Watchdog(Exception):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        message = "Error wdt"
        super().__init__(message)
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        log.error("Problems? %s", sys.exc_info())
        log.error("Reseting script due to timeout wdt")
        os.execv(sys.executable, ['python'] + sys.argv)
        raise self
