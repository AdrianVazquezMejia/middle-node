import os
import sys
from threading import Timer


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
        print("Reseting script due to crashed")
        os.execv(sys.executable, ['python'] + sys.argv)
        raise self
