#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class which detects whether computing nodes happens error or not.
##########################################################


import ConfigParser
import logging
import os
import sys

from HostFailures import HostFailures
from InstanceFailures import InstanceFailure
from ReceiveInfoFromController import ReceiveInfoFromController

config = ConfigParser.RawConfigParser()
config.read('hass_node.conf')
log_level = logging.getLevelName(config.get("log", "level"))
log_file_name = config.get("log", "location")
dir = os.path.dirname(log_file_name)
if not os.path.exists(dir):
    os.makedirs(dir)
FORMAT = "%(asctime)s [%(levelname)s] : %(message)s"
logging.basicConfig(filename = log_file_name, level = log_level, format = FORMAT)


def main():
    # agent = DetectionAgent()
    # agent.startListen()
    host_detection = HostFailures()
    host_detection.daemon = True
    host_detection.start()
    recv = ReceiveInfoFromController()
    recv.daemon = True
    recv.start()
    instance_detection = InstanceFailure()
    instance_detection.daemon = True
    instance_detection.start()
    # asyncore.loop()
    try:
        while True:
            pass
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
