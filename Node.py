from NovaClient import NovaClient
#from DetectionManager import DetectionManager


class Node (object):
	def __init__(self, node_id , name , cluster_id):
		self.node_id = node_id
		self.cluster_id = cluster_id
		self.name = name
		self.nova_client = NovaClient.getInstance()
		self.instance_list = []
		#self.detect = DetectionManager()

	def getInstanceList(self):
		pass
	def isInComputePool(self):
		return self.name in self.nova_client.getComputePool()
	def addInstance(self , instanceId):
		pass
	def deleteInstance(self , instanceId):
		pass
	def startDetection(self):
		self.detect.pollingRegister(self.node_id , name)

if __name__ == "__main__":
	a = Node("123","compute2")
	print a.isInComputePool()