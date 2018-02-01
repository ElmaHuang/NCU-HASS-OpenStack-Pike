import ConfigParser
import asyncore
import logging
import sys

from HostFailures import HostFailures
from InstanceFailures import InstanceFailure
from ReceiveInfoFromController import ReceiveInfoFromController


class DetectionAgent():
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('hass_node.conf')

        log_level = logging.getLevelName(config.get("log", "level"))
        log_file_name = config.get("log", "location")
        FORMAT = "%(asctime)s [%(levelname)s] : %(message)s"
        logging.basicConfig(filename=log_file_name, level=log_level, format=FORMAT)


def main():
    # agent = DetectionAgent()
    # agent.startListen()
    host_detection = HostFailures()
    recv = ReceiveInfoFromController()
    recv.daemon = True
    recv.start()
    instance_detection = InstanceFailure()
    instance_detection.daemon = True
    instance_detection.start()
    asyncore.loop()
    try:
        while True:
            pass
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
