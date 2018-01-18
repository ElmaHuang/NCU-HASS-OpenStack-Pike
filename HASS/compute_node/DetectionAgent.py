import socket
import asyncore
import sys
import ConfigParser
import xmlrpclib
import time
from ReceiveInfoFromController import ReceiveInfoFromController
from HostFailures import HostFailures
from InstanceFailures import InstanceFailure


class DetectionAgent():
    def __init__(self):
        pass


def main():
    # agent = DetectionAgent()
    # agent.startListen()
    host_detection = HostFailures()
    recv = ReceiveInfoFromController()
    recv.start()
    instance_detection = InstanceFailure()
    instance_detection.start()
    asyncore.loop()
    try:
        while True:
            pass
    except:
        sys.exit(1)


if __name__ == "__main__":
    main()
