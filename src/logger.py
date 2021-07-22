import logging
import sys

dateformat = "%m/%d/%Y  %H:%M:%S"
logformat = "%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s"
consoleforma = "[%(levelname)-5.5s] [%(name)s] %(message)s"


def build_logger():
    """! Design the structure of the logger and the 
        way is going to be registered

    @return log         register of information and the message
    """
    logFormatter = logging.Formatter(logformat, datefmt=dateformat)
    consoleFormatter = logging.Formatter(
        "[%(levelname)-5.5s] [%(name)s] %(message)s")
    log = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "logs"))
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    log.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(consoleFormatter)
    consoleHandler.setLevel(logging.INFO)
    log.addHandler(consoleHandler)

    log.setLevel(logging.DEBUG)
    print(type(log))
    return log
