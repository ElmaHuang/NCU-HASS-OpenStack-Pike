#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a interface for node data structure.
#########################################################
from NovaClient import NovaClient
from DetectionThread import DetectionThread
from IPMIModule import IPMIManager
import ConfigParser
import socket


class NodeInterface(object):
    def __init__(self, name, cluster_id):
        self.name = name
        # self.protected_instance_list = []
        self.cluster_id = cluster_id
        self.ipmi = IPMIManager()
        self.ipmi_status = self.ipmi._getIPMIStatus(self.name)
        self.nova_client = NovaClient.getInstance()
        self.detection_thread = None
        self.initDetectionThread()

    def setNodeName(self, name):
        self.name = name

    def getNodeName(self):
        return self.name

    def setClusterId(self, cluster_id):
        self.cluster_id = cluster_id

    def getClusterId(self, cluster_id):
        return self.cluster_id

    def initDetectionThread(self):
        config = ConfigParser.RawConfigParser()
        config.read('hass.conf')

        cluster_id = self.cluster_id
        node = self
        polling_port = int(config.get("detection", "polling_port"))
        # ipmi_status = self.ipmi_status
        polling_interval = float(config.get("detection", "polling_interval"))
        self.detection_thread = DetectionThread(cluster_id, node, polling_port, polling_interval)

    def startDetectionThread(self):
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def deleteDetectionThread(self):
        self.detection_thread.stop()

    def getInfo(self):
        return [self.name, self.cluster_id, self.ipmi_status]

    def sendUpdateInstance(self):
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.connect((self.name, 5001))
        # ip = so.recv(1024)
        so.send("update instance")
        so.close()


if __name__ == "__main__":
    a = NodeInterface("compute1", "23")
    a.startDetectionThread()
    while True:
        pass
