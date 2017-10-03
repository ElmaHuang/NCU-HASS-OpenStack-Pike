from NodeInterface import NodeInterface
from Instance import Instance
from IPMIModule import IPMIManager
#from DetectionManager import DetectionManager


class Node (NodeInterface):
	def __init__(self, id , name , cluster_id, ipmi_status):
		super(Node, self).__init__(id, name , cluster_id, ipmi_status)
		self.ipmi_module = IPMIManager()

	def getProtectedInstanceList(self):
		return self.protected_instance_list

	def addInstance(self , instance_id):
		if self.isProtected(instance_id): # check instance is already being protected
			raise Exception("this instance is already being protected!")
		instance = Instance(id=instance_id, 
							name=self.nova_client.getInstanceNameById(instance_id), 
							host=self.name)

		if not instance.isIllegal(): # check instance is running and has volume or not
			raise Exception("this instance may either have not running or has no volume")
		self.protected_instance_list.append(instance)

	def deleteInstance(self , instance_id):
		if not self.isProtected(instance_id):
			raise Exception("this instance is not being protected")
		for instance in self.protected_instance_list:
			if instance.id == instance_id:
				self.protected_instance_list.remove(instance)
				break
		return True

	def containsInstance(self, instance_id):
		node_instance_list = self.nova_client.getInstanceListByNode(self.name)
		for instance in node_instance_list:
			id = getattr(instance , "id")
			if id == instance_id:
				return True
		return False

	def getInstanceInfo(self):
		res = []
		for instance in self.protected_instance_list:
			res.append(instance.getInfo())
		return res

	def isProtected(self, instance_id):
		for instance in self.protected_instance_list:
			if instance.id == instance_id:
				return True
		return False

	def boot(self):
		ipmi_module.startNode(self.id)

	def shutdown(self):
		ipmi_module.shutOffNode(self.id)

	def reboot(self):
		ipmi_module.rebootNode(self.id)

	def evacuateInstances(self):
		pass

	def isInComputePool(self):
		return self.name in self.nova_client.getComputePool()

if __name__ == "__main__":
	a = Node("123","compute1", "23123")
	print a.getInstanceList()
	print a.getInstanceList()[1].isIllegal()