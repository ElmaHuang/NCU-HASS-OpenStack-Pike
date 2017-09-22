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
		self.nova_client = NovaClient.getInstance()
		self.db = DatabaseManager()

	def addNode(self , node_name_list , write_DB = True):
		code = ""
		message = ""
		# create node list
		tmp = []
		for node_name in node_name_list:
			node_id = str(uuid.uuid4())
			node = Node(node_id = node_id , name = node_name , cluster_id = self.uuid)
			tmp.append(node)
		# check node is illegal
		if not self._nodeIsIllegal(tmp):
			code = "1"
			message = "Cluster add node fail , maybe overlapping or not in compute pool please check again!"
			logging.info("Cluster add node fail , maybe overlapping or not in compute pool please check again!")
			result = {"code":code, "clusterId":self.uuid, "message":message}
			return result
		# add node
		for node in tmp:
			self.node_list.append(node)
			#node.startDetection()
			if not write_DB:
				message += node.name + " sync from DB \n"
				continue
			# start write to DB
			try:
				db_uuid = self.uuid.replace("-","")
				data = {"node_name": node.name,"below_cluster":db_uuid}
				self.db.writeDB("ha_node" , data)
				code = "0"
				message = "The node %s is added to cluster." % self.getAllNodeStr()
			except Exception as e:
				print str(e)
				logging.error("Cluster addnode - Access database failed.")
				code = "1"
				message = "Access database failed."
		result = {"code":code, "clusterId":self.uuid, "message":message}
		return result

	def _nodeIsIllegal(self , unchecked_nodes):
		for unchecked_node in unchecked_nodes:
			if not ( unchecked_node.isInComputePool() and # check node is in compute pool
					 self._isNodeDuplicate(unchecked_node) ): # check node is duplicate
				return False
		return True

	def _isNodeDuplicate(self , unchecked_node):
		for node in self.node_list:
			if node.name == unchecked_node.name:
				return False
		return True

	def getNodeList(self):
		return self.node_list

	def getAllNodeStr(self):
		ret = ""
		for node in self.node_list:
			ret += node.name
		return ret

	def removeNode():
		pass

