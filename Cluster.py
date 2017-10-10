from ClusterInterface import ClusterInterface
from DetectionManager import DetectionManager
from Node import Node
import uuid
import logging
import ConfigParser

class Cluster(ClusterInterface):
	def __init__(self, id , name):
		super(Cluster, self).__init__(id, name)

	def addNode(self, node_name_list):
		# create node list
		try:
			message=""
			result=None
			for node_name in node_name_list:
				if  not self._nodeIsIllegal(node_name) :
					#id = str(uuid.uuid4())
					ipmi_status = self._getIPMIStatus(node_name)
					node = Node(name = node_name , cluster_id = self.id , ipmi_status = ipmi_status)
					self.node_list.append(node)
					#node.startDetection()
					message = "The node %s is added to cluster." % self.getAllNodeStr()
					result = {"code": "0", "clusterId": self.id, "message": message}
			logging.info(message)
			return result

		except:
			message = "Cluster add node fail , some node maybe overlapping or not in compute pool please check again! The node list is %s." % (self.getAllNodeStr() + ",")
			logging.error(message)
			result = {"code": "1", "clusterId": self.id, "message": message}
			return result

	def deleteNode(self , node_name):
		node = self.getNodeByName(node_name)
		if not node:
			raise Exception("Delete node : Not found the node %s" % node_name)
		#node.deleteDetectionThread()
		self.node_list.remove(node)

	def getAllNodeInfo(self):
		ret = []
		for node in self.node_list:
			ret.append(node.getInfo())
		return ret

	def findNodeByInstance(self, instance_id):
		for node in self.node_list:
			if node.containsInstance(instance_id):
				return node
		return None

	'''
	def _isNodeDuplicate(self , unchecked_node_name):
		for node in self.node_list:
			if node.name == unchecked_node_name:
				return True
		return False
	'''

	def _isInComputePool(self, unchecked_node_name):
		return unchecked_node_name in self.nova_client.getComputePool()

	def _nodeIsIllegal(self , unchecked_node_name):
		if not self._isInComputePool(unchecked_node_name):
			return True
		#if self._isNodeDuplicate(unchecked_node_name):
			#return True
		return False

	#be DB called
	def getNodeList(self):
		return self.node_list
	'''
	def getNodeById(self, node_id):
		#node_list = self.getNodeList()
		for node in self.node_list:
			if node.id == node_id:
				return node
		return None
	'''

	def getNodeByName(self, name):
		#node_list = self.getNodeList()
		for node in self.node_list:
			if node.name == name:
				return node
		return None

	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name
		return ret


	def deleteAllNode(self):
		for node in self.node_list:
			self.deleteNode(node.id)
	'''
	def getInfo(self):
		return [self.id, self.name]
	'''


	def getProtectedInstanceList(self):
		ret = []
		#node_list = self.getNodeList()
		for node in self.node_list:
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
		#node_list = self.getNodeList()
		print "node list of cluster:",self.node_list
		for node in self.node_list:
			if node.containsInstance(instance_id):
				return True
		return False

	def _getIPMIStatus(self, node_id):
		config = ConfigParser.RawConfigParser()
		config.read('hass.conf')
		ip_dict = dict(config._sections['ipmi'])
		return node_id in ip_dict

