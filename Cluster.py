from ClusterInterface import ClusterInterface
from DetectionManager import DetectionManager
from Node import Node
from Instance import Instance
import uuid
import logging
import ConfigParser

class Cluster(ClusterInterface):
	def __init__(self, id , name):
		super(Cluster, self).__init__(id, name)

	def addNode(self, node_name_list, fail=False):
		code = ""
		message = ""
		# create node list
		for node_name in node_name_list:
			if not self._nodeIsIllegal(node_name):
				node = Node(name = node_name , cluster_id = self.id)
				self.node_list.append(node)
				node.startDetectionThread()
			else:
				fail = True
		if fail:
			code = "1"
			message = "Cluster add node fail , some node maybe overlapping or not in compute pool please check again! current node list is %s." % (self.getAllNodeStr()+",")
			logging.info("Cluster add node fail , maybe overlapping or not in compute pool please check again!")
			result = {"code":code, "clusterId":self.id, "message":message}
			return result
		else:
			code = "0"
			message = "The node %s is added to cluster." % self.getAllNodeStr()
			result = {"code":code, "clusterId":self.id, "message":message}
			return result

	def _isNodeDuplicate(self , unchecked_node_name):
		for node in self.node_list:
			if node.name == unchecked_node_name:
				return True
		return False
	def _isInComputePool(self, unchecked_node_name):
		return unchecked_node_name in self.nova_client.getComputePool()

	def _nodeIsIllegal(self , unchecked_node_name):
		if not self._isInComputePool(unchecked_node_name):
			return True
		return False

	def deleteNode(self , node_name):
		node = self.getNode(node_name)
		if not node:
			raise Exception("Delete node : Not found the node %s" % node_name)
		#node.deleteDetectionThread()
		self.node_list.remove(node)

	def deleteAllNode(self):
		for node in self.node_list:
			self.deleteNode(node.name)


	def addInstance(self, instance_id):
		if not self.checkInstanceExist(instance_id): # check instance is exist
			raise Exception("this instance not exist") 
		if not self.nova_client.isInstancePowerOn(instance_id): # check is power on
			raise Exception("this instance is not running!")
		if not self.nova_client.isInstanceGetVolume(instance_id): # check has volume
			raise Exception("this instance not having volume!")

		instance = Instance(id=instance_id, 
							name=self.nova_client.getInstanceName(instance_id), 
							host=self.nova_client.getInstanceHost(instance_id))

		self.protected_instance_list.append(instance)

	def deleteInstance(self, instance_id):
		if not self.isProtected(instance_id):
			raise Exception("this instance is not being protected")
		for instance in self.protected_instance_list:
			if instance.id == instance_id:
				self.protected_instance_list.remove(instance)
				break

	def updateInstance(self):
		for instance in self.protected_instance_list:
			host = self.nova_client.getInstanceHost(instance.id)
			instance.host = host

	def isProtected(self, instance_id):
		for instance in self.protected_instance_list:
			if instance.id == instance_id:
				return True
		return False

	def findNodeByInstance(self, instance_id):
		for node in self.node_list:
			if node.containsInstance(instance_id):
				return node
		return None

	def getNodeList(self):
		return self.node_list

	def getNode(self, name):
		node_list = self.getNodeList()
		for node in node_list:
			if node.name == name:
				return node
		return None

	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name
		return ret

	def getInfo(self):
		return [self.id, self.name]

	def getAllNodeInfo(self):
		ret = []
		for node in self.node_list:
			ret.append(node.getInfo())
		return ret

	def getProtectedInstanceList(self):
		return self.protected_instance_list

	def getProtectedInstanceListByNode(self, node):
		ret = []
		protected_instance_list = self.getProtectedInstanceList()
		for instance in protected_instance_list:
			if instance.host == node.name:
				ret.append(instance)
		return ret

	def getAllInstanceInfo(self):
		ret = []
		instance_list = self.getProtectedInstanceList()
		for instance in instance_list:
			ret.append(instance.getInfo())
		return ret

	def nodeExist(self, node_name):
		node_list = self.getNodeList()
		for node in node_list:
			if node.name == node_name:
				print node.name
				return True

	def checkInstanceExist(self, instance_id):
		node_list = self.getNodeList()
		for node in node_list:
			if node.containsInstance(instance_id):
				return True
		return False

	def findTargetHost(self, fail_node):
		import random
		target_list = [node for node in self.node_list if node != fail_node]
		target_host = random.choice(target_list)
		return target_host

	def evacuate(self, instance, target_host, fail_node):
		self.nova_client.evacuate(instance, target_host, fail_node)


