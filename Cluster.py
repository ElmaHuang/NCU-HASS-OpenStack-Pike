from ClusterInterface import ClusterInterface
#from DetectionManager import DetectionManager
from Node import Node
import uuid
import logging

class Cluster(ClusterInterface):
	def __init__(self , id , name):
		super(Cluster, self).__init__(id, name)

	def addNode(self , node_name_list ):
		try:
			for node in node_name_list:
				if not self._nodeIsIllegal(node):
					node_name_list.remove(node)

			for node_name in node_name_list:
				node = Node(id= None,name=node_name, cluster_id= self.id )
				self.node_list.append(node)

			# self.nodeList.extend(nodeList)
			result = {"code": "0", "clusterId": self.id,
					  "message": "The node %s is added to cluster." % node_name_list}
			return result
		except:
			logging.info("Cluster add node fail , maybe overlapping or not in compute pool please check again!")
			result = {"code": "1", "clusterId": self.id,"message": "Cluster add node fail , some node maybe overlapping or not in compute pool please check again! The node list is %s." % node_name_list}
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

	def _isInComputePool(self, node_name):
		return node_name in self.nova_client.getComputePool()

	def _nodeIsIllegal(self , unchecked_node):
		if not self._isInComputePool(unchecked_node):
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


