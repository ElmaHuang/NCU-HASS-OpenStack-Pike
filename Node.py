from NodeInterface import NodeInterface
from Instance import Instance
from IPMIModule import IPMIManager
#from DetectionManager import DetectionManager


class Node (NodeInterface):
	def __init__(self, name, cluster_id, ipmi_status):
		super(Node, self).__init__(name , cluster_id, ipmi_status)
		self.ipmi_module = IPMIManager()

	def containsInstance(self, instance_id):
		node_instance_list = self.nova_client.getInstanceListByNode(self.name)
		for instance in node_instance_list:
			id = getattr(instance , "id")
			print id
			if id == instance_id:
				return True
		return False

	def getInstanceInfo(self):
		res = []
		for instance in self.protected_instance_list:
			res.append(instance.getInfo())
		return res

	def boot(self):
		ipmi_module.startNode(self.id)

	def shutdown(self):
		ipmi_module.shutOffNode(self.id)

	def reboot(self):
		ipmi_module.rebootNode(self.id)

	def evacuateInstances(self):
		pass

if __name__ == "__main__":
	a = Node("123","compute1", "23123")
	print a.getInstanceList()
	print a.getInstanceList()[1].isIllegal()