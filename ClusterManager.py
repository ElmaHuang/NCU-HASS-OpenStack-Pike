from Cluster import Cluster
from DatabaseManager import DatabaseManager
import uuid
import logging

class ClusterManager():
	_cluster_dict = None
	_db = None
	_RESET_DB = True

	@staticmethod
	def init():
		ClusterManager._cluster_dict = {}
		ClusterManager._db = DatabaseManager()
		ClusterManager._db.createTable()
		ClusterManager.syncFromDatabase()

	@staticmethod
	def createCluster(cluster_name, cluster_id = None, write_DB = True):
		if ClusterManager._isOverLapping(cluster_name):
			logging.error("ClusterManager - cluster name overlapping")
			result = {"code": "1", "clusterId":None, "message":"cluster overlapping abort!"}
			return result
		result = ClusterManager._addToClusterList(cluster_name , cluster_id)
		if write_DB:
			ClusterManager.syncToDatabase()
		return result

	@staticmethod
	def deleteCluster(cluster_id , write_DB = True):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			code = "1"
			message = "delete cluster fail. The cluster is not found. (cluster_id = %s)" % cluster_id
			result = {"code": code, "clusterId":cluster_id, "message":message}
			return result
		cluster.deleteAllNode()
		del ClusterManager._cluster_dict[cluster_id]

		if write_DB:
			ClusterManager.syncToDatabase()
		code = "0"
		message = "delete cluster success. The cluster is deleted. (cluster_id = %s)" % cluster_id
		result = {"code": code, "clusterId":cluster_id, "message":message}
		return result

	@staticmethod
	def getClusterList():
		return ClusterManager._cluster_dict

	@staticmethod
	def listCluster():
		res = []
		for id , cluster in ClusterManager._cluster_dict.iteritems():
			res.append((cluster.getInfo()))
		return res

	@staticmethod
	def addNode(cluster_id, node_name_list, write_DB = True):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			code = "1"
			message = "Add the node to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
			result = {"code": code, "clusterId":cluster_id, "message":message}
			return result
		result = cluster.addNode(node_name_list)
		if write_DB:
			ClusterManager.syncToDatabase()
		return result

	@staticmethod
	def deleteNode(cluster_id, node_name , write_DB=True):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			code = "1"
			message = "delete the node failed. The cluster is not found. (cluster_id = %s)" % cluster_id
			result = {"code": code, "clusterId":cluster_id, "message":message}
			return result
		try:
			cluster.deleteNode(node_name)
			if write_DB:
				ClusterManager.syncToDatabase()
			code = "0"
			message = "delete the node success. node is deleted. (node_name = %s)" % node_name
			result = {"code": code, "clusterId":cluster_id, "message":message}
			return result
		except:
			code = "1"
			message = "delete node fail. node not found. (node_name = %s)" % node_name
			result = {"code": code, "clusterId":cluster_id, "message":message}
		return result

	@staticmethod
	def listNode(cluster_id):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			raise Exception("cluster not found")
		result = cluster.getAllNodeInfo()
		return result

	@staticmethod
	def addInstance(cluster_id, instance_id):
		code = ""
		message = "" 

		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			code = "1"
			message = "Add the instance to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
			result = {"code": code, "clusterId":cluster_id, "message":message}
			return result
		cluster.addInstance(instance_id)
		# log message
		code = "0"
		message = "Add instance success , instance_id : %s , cluster_id : %s" % (instance_id , cluster_id) 
		result = {"code": code, "clusterId":cluster_id, "message":message}
		return result

	@staticmethod
	def deleteInstance(cluster_id , instance_id):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			code = "1"
			message = "Add the instance to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
		try:
			cluster.deleteInstance(instance_id)
			code = "0"
			message = "delete instance success. this instance is now deleted (instance_id = %s)" % instance_id
		except Exception as e:
			print str(e)
			code = "1"
			message = "delete instance failed. this instance is not being protected (instance_id = %s)" % instance_id
		result = {"code": code, "clusterId":cluster_id, "message":message}
		return result

	@staticmethod
	def getProtectedInstanceList(cluster_id):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			raise Exception("get instance list fail , not find the cluster %s" % cluster_id)
		return cluster.getProtectedInstanceList()

	@staticmethod
	def listInstance(cluster_id):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			raise Exception("get instance list fail , not find the cluster %s" % cluster_id)
		return cluster.getAllInstanceInfo()

	@staticmethod
	def _addToClusterList(cluster_name , cluster_id = None):
		result = None
		if cluster_id:
			cluster = Cluster(id = cluster_id , name = cluster_name)
			ClusterManager._cluster_dict[cluster_id] = cluster
		else:
			#start add to list
			cluster_id = str(uuid.uuid4())
			cluster = Cluster(id = cluster_id , name = cluster_name)
			ClusterManager._cluster_dict[cluster_id] = cluster
			result = {"code": "0", "clusterId":cluster_id, "message":"create cluster success"}
			return result

	@staticmethod
	def getCluster(cluster_id):
		if not ClusterManager._isCluster(cluster_id):
			logging.info("cluster not found id %s" % cluster_id)
			return None
		return ClusterManager._cluster_dict[cluster_id]

	@staticmethod
	def _isOverLapping(name):
		for cluster_id , cluster in ClusterManager._cluster_dict.items():
			if cluster.name == name:
				return True
		return False

	@staticmethod
	def _isCluster(cluster_id):
		if cluster_id in ClusterManager._cluster_dict:
			return True
		return False

	@staticmethod
	def reset(reset_DB=_RESET_DB):
		if reset_DB:
			ClusterManager._db.resetAll()
		ClusterManager._cluster_dict = {}


	@staticmethod
	def syncFromDatabase():
		ClusterManager._db.syncFromDB(ClusterManager)

	@staticmethod
	def syncToDatabase():
		ClusterManager._db.syncToDB(ClusterManager)



if __name__ == "__main__":
	ClusterManager.init()
	ClusterManager.deleteCluster("8c46ecee-9bd6-4c82-b7c8-6b6d20dc09d7")

