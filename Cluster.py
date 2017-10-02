from DetectionManager import DetectionManager
from NovaClient import NovaClient
from DatabaseManager import DatabaseManager
from Node import Node
import uuid
import logging

class Cluster(object):
	def __init__(self , uuid , name):
		self.uuid = uuid
		self.name = name
		self.node_list = []
		self.nova_client = NovaClient()
		self.detect = DetectionManager()
		self.db = DatabaseManager()

	def addNode(self , node_name_list , write_DB = True):
		try:
			for node in node_name_list:
				if not self._nodeIsIllegal(node):
					node_name_list.remove(node)

			for node_name in node_name_list:
				node = Node(name=node_name, cluster_id=self.uuid)
				self.node_list.append(node)

			if write_DB:
				for node in node_name_list:
					self.detect.pollingRegister(self.uuid, node, write_DB)
			# self.nodeList.extend(nodeList)
			result = {"code": "0", "clusterId": self.uuid, "message": "The node %s is added to cluster." % node_name_list}
			return result
		except:
			logging.info("Cluster add node fail , maybe overlapping or not in compute pool please check again!")
			result = {"code": "1", "clusterId": self.uuid,"message": "Cluster add node fail , some node maybe overlapping or not in compute pool please check again! The node list is %s." % nodeList}
			return result

	def deleteNode(self):
		pass

	def _nodeIsIllegal(self , unchecked_node):
		if not self.isInComputePool(unchecked_node):
			return False
		if self._isNodeDuplicate(unchecked_node):
			return False
		
		return True

	def _isNodeDuplicate(self , unchecked_node):
		for node in self.node_list:
			if node.name == unchecked_node.name:
				return True
		return False

	def isInComputePool(self, node_name):
		return node_name in self.nova_client.getComputePool()

	def getNodeList(self):
		return self.node_list
'''
	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name
		return ret
'''

