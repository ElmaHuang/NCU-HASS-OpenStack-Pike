from NovaClient import NovaClient
from DetectionThread import DetectionThread
import ConfigParser

class NodeInterface(object):

	def __init__(self ,name, cluster_id , ipmi_status):
		#self.id = id
		self.name = name
		self.protected_instance_list = []
		self.cluster_id = cluster_id
		self.ipmi_status = ipmi_status
		self.nova_client = NovaClient.getInstance()
		self.detection_thread = None
		#self.initDetectionThread()
	
	#def setNodeId(self, id):
		#self.id = id

	#def getNodeId(self):
		#return self.id

	def setNodeName(self, name):
		self.name = name

	def getNodeName(self):
		return self.name

	def setClusterId(self, cluster_id):
		self.cluster_id = cluster_id

	def getClusterId(self, cluster_id):
		return self.cluster_id 

	#def addInstance(self, instance):
		#self.protected_instance_list.append(instance)

	#def removeInstance(self, instance):
		#self.instance_list.remove(instance)

	#def initInstanceList(self):
		#self.instance_list = []

	def initDetectionThread(self):
		config = ConfigParser.RawConfigParser()
		config.read('hass.conf')

		polling_interval = config.get("detection","polling_interval")
		polling_threshold = config.get("detection","polling_threshold")
		cluster_id = self.cluster_id
		node = self.name
		polling_port = int(config.get("detection","polling_port"))
		wait_restart_threshold = int(config.get("detection","wait_restart_threshold"))
		ipmi_status = self.ipmi_status

		self.detection_thread = DetectionThread(polling_interval, polling_threshold, cluster_id, 
												node, polling_port, wait_restart_threshold, 
												ipmi_status)

	def startDetectionThread(self):
		self.detection_thread.daemon = True
		self.detection_thread.start()
	
	def deleteDetezctionThread(self):
		self.detection_thread.stop()
		
	def getInfo(self):
		return [self.name , self.cluster_id]

if __name__ == "__main__":
	a = NodeInterface("compute1" , "23" , True)
	a.startDetectionThread()
	while True:
		pass
