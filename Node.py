from NodeInterface import NodeInterface
from Instance import Instance
#from IPMIModule import IPMIManager
from DetectionThread import DetectionThread


class Node (NodeInterface):
	def __init__(self, name , cluster_id):
		super(Node, self).__init__(name , cluster_id)
		#self.ipmi_module = IPMIManager()

	'''
	def getProtectedInstanceList(self):
		return self.instance_listnam
	'''

	def containsInstance(self, instance_id):
		node_instance_list = self.nova_client.getInstanceListByNode(self.name)
		for instance in node_instance_list:
			id = getattr(instance , "id")
			#print instance_id,id
			if id == instance_id:
				return True
		return False

	'''
	def getInstanceInfo(self):
		res = []
		for instance in self.protected_instance_list:
			res.append(instance.getInfo())
		return res
	
	def boot(self):
		self.ipmi_module.startNode(self.name)

	def shutdown(self):
		self.ipmi_module.shutOffNode(self.name)

	def reboot(self):
		self.ipmi_module.rebootNode(self.name)

	def evacuateInstances(self):
		pass
	
	def isInComputePool(self):
		return self.name in self.nova_client.getComputePool()
	'''

if __name__ == "__main__":
	pass
	#a = Node("123","compute1", "23123")
	#print a.getInstanceList()
	#print a.getInstanceList()[1].isIllegal()