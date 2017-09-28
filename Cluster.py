from ClusterInterface import ClusterInterface
from DetectionManager import DetectionManager
from Node import Node
import uuid
import logging

class Cluster(ClusterInterface):
	def __init__(self , id , name):
		super(Cluster, self).__init__(id, name)

	def addNode(self , node_name_list , write_DB = True):
		code = ""
		message = ""
		fail = False
		# create node list
		tmp = []
		for node_name in node_name_list:
			id = str(uuid.uuid4())
			node = Node(id = id , name = node_name , cluster_id = self.id)
			tmp.append(node)
		# check node is illegal

		correct_node = []
		for unchecked_node in tmp:
			if self._nodeIsIllegal(unchecked_node):
				correct_node.append(unchecked_node)
			else:
				fail = True
		# add node
		for node in correct_node:
			self.node_list.append(node)
			#node.startDetection()
			if not write_DB:
				message += node.name + " sync from DB \n"
				continue
		if fail:
			code = "1"
			message = "Cluster add node fail , some node maybe overlapping or not in compute pool please check again! The node list is %s." % (self.getAllNodeStr()+",")
			logging.info("Cluster add node fail , maybe overlapping or not in compute pool please check again!")
			result = {"code":code, "clusterId":self.id, "message":message}
			return result
		else:
			code = "0"
			message = "The node %s is added to cluster." % self.getAllNodeStr()
			result = {"code":code, "clusterId":self.id, "message":message}
			return result

	def findNodeByInstance(self, instance_id):
		for node in self.node_list:
			if node.containsInstance(instance_id):
				return node
		return None

	def _isNodeDuplicate(self , unchecked_node):
		for node in self.node_list:
			if node.name == unchecked_node.name:
				return True
		return False

	def _nodeIsIllegal(self , unchecked_node):
		if not unchecked_node.isInComputePool():
			return False
		if self._isNodeDuplicate(unchecked_node):
			return False
		return True

	def getNodeList(self):
		return self.node_list

	def getNode(self , node_id):
		node_list = self.getNodeList()
		for node in node_list:
			if node.id == node_id:
				return node
		return None

	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name
		return ret

	def deleteNode(self , node_id):
		node = self.getNode(node_id)
		if not node:
			raise Exception("Delete node : Not found the node %s" % node_id)
		#node.deleteDetectionThread()
		self.node_list.remove(node)

	def deleteAllNode(self):
		for node in self.node_list:
			self.deleteNode(node.id)

	def getInfo(self):
		return [self.id, self.name]

	def getAllNodeInfo(self):
		ret = []
		for node in self.node_list:
			ret.append(node.getInfo())
		return ret

	def getProtectedInstanceList(self):
		ret = []
		node_list = self.getNodeList()
		for node in node_list:
			instance_list = node.getProtectedInstanceList()
			for instance in instance_list:
				ret.append(instance)
		return ret

	def getAllInstanceInfo(self):
		ret = []
		instance_list = self.getProtectedInstanceList()
		for instance in instance_list:
			ret.append(instance.getInfo())
		return ret

	def checkInstanceExist(self, instance_id):
		node_list = self.getNodeList()
		print node_list
		for node in node_list:
			if node.containsInstance(instance_id):
				return True
		return False


