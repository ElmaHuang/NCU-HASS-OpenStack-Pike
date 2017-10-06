from ClusterManager import ClusterManager
from Schedule import Schedule
from NovaClient import NovaClient

import logging

class RecoverManager(object):
	def __init__(self):
		self.nova_client = NovaClient.getInstance()

	def recoverOSHang(self, cluster_id, fail_node):
		self.revocerVM(cluster_id, fail_node)
		result = fail_node.reboot()
		if result["code"] == "0":
			logging.info(message + result["message"])


		pass
	def recoverNodeCrash(self):
		pass
	def recoverNetworkIsolation(self):
		pass
	def recoverSensorCritical(self):
		pass
	def recoverServiceFail(self):
		pass

	def revocerVM(self, cluster_id, fail_node):
		cluster = ClusterManager.getCluster(cluster_id)
		if not cluster:
			logging.error("RecoverManager : cluster not found")
			return
		if len(cluster.getNodeList()) < 2:
			logging.error("RecoverManager : evacuate fail, cluster only one node")
			return
		if not fail_node:
			logging.error("RecoverManager : not found the fail node")
			return

		protected_instance_list = cluster.getProtectedInstanceList()
		for instance in protected_instance_list:
			if instance.host = fail_node.name:
				target_host = cluster.findTargetHost(fail_node)
				if not target_host:
					logging.error("RecoverManager : not found the target_host %s" % target_host)
					continue
				try:
					cluster.evacuate(instance, target_host, fail_node)
				except Exception as e:
					print str(e)
					logging.error("RecoverManager - The instance %s evacuate failed" % instance.id)
		self._check_vm_status(fail_node, cluster)
		cluster.updateInstance()

	def _check_vm_status(self, fail_node, cluster, check_timeout=60):
		status = False
		ret = True
		instance_list = cluster.getProtectedInstanceList()
		for instance in instance_list:
			if instance.host = node.name:
				openstack_instance = self.nova_client.getVM(instance.id)
				ip = str(instance.networks['provider'][0])
				check_timeout = 60

				while check_timeout > 0:
					try:
						response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1' , ip], stderr=subprocess.STDOUT, universal_newlines=True)
						status = True
						break
					except subprocess.CalledProcessError:
						status = False
					finally:
						time.sleep(1)
						check_timeout -= 1

				if status == False:
					logging.error("vm %s cannot ping" % instance.name)
					ret = False
		return ret




