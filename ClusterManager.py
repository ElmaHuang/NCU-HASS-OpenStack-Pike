from Cluster import Cluster
from DatabaseManager import DatabaseManager
import uuid
import logging

class ClusterManager(object):

	def __init__(self):
		self.cluster_list = {}
		self.db = DatabaseManager()
		self.db.createTable()
		self.syncFromDatabase()

	def syncFromDatabase(self):
		self.reset()
		exist_cluster=self.db.syncFromDB()
		for cluster in exist_cluster:
			self.createCluster(exist_cluster["cluster_name"],exist_cluster["cluster_id",False])
			self.addNode(exist_cluster["cluster_id"],exist_cluster["node_list"],False)

	def syncToDatabase(self):
		cluster_list = self.getClusterList()
		self.db.syncToDB(cluster_list)

	def createCluster(self , cluster_name , cluster_id = None,write_DB = True):
		#result = None
		if self._isOverLapping(cluster_name):
			logging.error("ClusterManager - cluster name overlapping")
			result = {"code": "1", "clusterId":None, "message":"cluster overlapping abort!"}
			return result
		#result = self._addToCluster(cluster_name)
		result = self._addToCluster(cluster_name, cluster_id)
		if write_DB:
			self.syncToDatabase()
		return result

	def deleteCluster(self,cluster_id):
		result = None

		return result

	def listAllCluster(self):
		result = []
		for uuid, cluster in self.cluster_list.iteritems():
			result.append((uuid, cluster.name))
		return result

	def addNode(self , cluster_id , node_name_list , write_DB = True):
		cluster = self._getCluster(cluster_id)
		if not cluster:
			#code = "1"
			message = "Add the node to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
			result = {"code": "1", "clusterId":cluster_id, "message":message}
			return result
		result = cluster.addNode(node_name_list , write_DB)
		if write_DB:
			self.syncToDatabase()
		return result

	def deleteNode(self,cluster_id,node_name,wirte_DB = True):
		pass

	def listAllNode(self,cluster_id):
		pass

	def getClusterList(self):
		return self.cluster_list

	def _addToCluster(self, cluster_name , cluster_id = None):
		result = None
		if cluster_id:
			cluster = Cluster(uuid = cluster_id , name = cluster_name)
			self.cluster_list[cluster_id] = cluster
		else:
			#start add to list
			cluster_id = str(uuid.uuid4())
			cluster = Cluster(uuid = cluster_id , name = cluster_name)
			self.cluster_list[cluster_id] = cluster
			#start write to DB
			try:
				db_uuid = cluster_id.replace("-","")
				data = {"cluster_uuid":db_uuid, "cluster_name":cluster_name}
				self.db.writeDB("ha_cluster", data)
				result = {"code": "0", "clusterId":cluster_id, "message":"create cluster success"}
			except:
				logging.error("Recovery Recovery - Access database failed.")
				result = {"code": "1", "clusterId":cluster_id, "message":"Access database failed, please wait a minute and try again."}
			return result

	def _getCluster(self,cluster_id):
		cluster = None
		try:
			cluster = self.cluster_list[cluster_id]
		except:
			logging.info("cluster not found id %s" % cluster_id)
		finally:
			return cluster

	def _isOverLapping(self , name):
		for cluster_id , cluster in self.cluster_list.items():
			if cluster.name == name:
				return True
		return False

	def reset(self):
		self.cluster_list = {}


if __name__ == "__main__":
	a = ClusterManager()
	print a.getClusterList()

