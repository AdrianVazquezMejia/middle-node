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
    """! Restart the system if there are some errors
   
    """
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        """! Initialize the Watchdog

        @param timeout            establish timeout time
        @param userHandler        define the value of the handler

        """
        message = "Error wdt"
        super().__init__(message)
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        """! Stop the timer and start it again
   
        """
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        """! Stop the timer
   
        """
        self.timer.cancel()

    def defaultHandler(self):
        """! Set a default handler to the Watchdog
   
        """
        log.error("Problems? %s", sys.exc_info())
        log.error("Reseting script due to timeout wdt")
        os.execv(sys.executable, ['python'] + sys.argv)
        raise self
