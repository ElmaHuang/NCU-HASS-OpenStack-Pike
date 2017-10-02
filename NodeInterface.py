from NovaClient import NovaClient

class NodeInterface(object):

	def __init__(self, id, name, cluster_id):
		self.id = id
		self.name = name
		self.protected_instance_list = []
		self.cluster_id = cluster_id
		self.nova_client = NovaClient.getInstance()
		#self.detection_thread = self.initDetectionThread()
	
	def setNodeId(self, id):
		self.id = id

	def getNodeId(self):
		return self.id

	def setNodeName(self, name):
		self.name = name

	def getNodeName(self):
		return self.name

	def setClusterId(self, cluster_id):
		self.cluster_id = cluster_id

	def getClusterId(self, cluster_id):
		return self.cluster_id 

	def addInstance(self, instance):
		self.protected.instance_list.append(instance)

	def removeInstance(self, instance):
		self.instance_list.remove(instance)

	def initInstanceList(self):
		self.instance_list = []

	def initDetectionThread(self):
		#self.detection_thread = new DetectionThread()
		pass
	
	def deleteDetezctionThread(self):
		self.detection_thread.stop()
		
	def getInfo(self):
		return [self.id , self.name , self.cluster_id]

if __name__ == "__main__":
	a = NodeInterface(123,"asdad" , "23")
	print a.id
	print a.name
	print a.cluster_id

