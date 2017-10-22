#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import ConfigParser
import time


class NovaClient (object):
	_instance = None # class reference
	_helper = None # novaclient reference

	def __init__(self):
		self.config = ConfigParser.RawConfigParser()
		self.config.read('hass.conf')
		if NovaClient._instance != None:
			raise Exception("This class is a singleton! , cannot initialize twice")
		else:
			self.initializeHelper()
			NovaClient._instance = self

	@staticmethod
	def getInstance():
		if not NovaClient._instance:
			NovaClient()
		if not NovaClient._helper:
			NovaClient._instance.initializeHelper()
		return NovaClient._instance

	def initializeHelper(self):
		NovaClient._helper = self.getHelper()
	
	def getHelper(self):
		auth = v3.Password(auth_url = 'http://controller:5000/v3',
						username = self.config.get("openstack", "openstack_admin_account"),
						password = self.config.get("openstack", "openstack_admin_password"),
						project_name = self.config.get("openstack", "openstack_admin_account"),
						user_domain_name = self.config.get("openstack", "openstack_user_domain_id"),
						project_domain_name = self.config.get("openstack", "openstack_project_domain_id"))
		sess = session.Session(auth = auth)
		novaClient = client.Client(2.25 , session = sess)
		return novaClient

	def getComputePool(self):
		computePool = []
		hypervisorList = self._getHostList()
		for hypervisor in hypervisorList:
			computePool.append(str(hypervisor.hypervisor_hostname))
		return computePool

	def _getHostList(self):
		return NovaClient._helper.hypervisors.list()

	def getVM(self,id):
		return NovaClient._helper.servers.get(id)

	def getInstanceListByNode(self, node_name):
		ret = []
		instance_list = self.getAllInstanceList()
		for instance in instance_list:
			name = getattr(instance, "OS-EXT-SRV-ATTR:hypervisor_hostname")
			if name == node_name:
				ret.append(instance)
		return ret

	def getInstanceState(self, instanceId):
		instance = self.getVM(instanceId)
		return getattr(instance, "status")

	def getAllInstanceList(self):
		return NovaClient._helper.servers.list(search_opts={'all_tenants': 1})

	def getInstanceNameById(self , instanceId):
		instance = self.getVM(instanceId)
		return getattr(instance, "OS-EXT-SRV-ATTR:instance_name")

	def getInstanceHost(self, instance_id):
		instance = self.getVM(instance_id)
		return getattr(instance, "OS-EXT-SRV-ATTR:host")

	def isInstanceExist(self, instanceId):
		try:
			NovaClient._helper.servers.get(instanceId)
		except:
			return False
		return True

	def isInstancePowerOn(self, id):
		vm = self.getVM(id)
		power_state = getattr(vm,"OS-EXT-STS:power_state")
		if power_state != 1:
			return False
		return True

	def getVolumes(self,id):
		return NovaClient._helper.volumes.get_server_volumes(id)

	def isInstanceGetVolume(self, id):
		volume = self.getVolumes(id)
		if volume == []:
			return False
		return True
		
	def novaServiceUp(self,node):
		return NovaClient._helper.services.force_down(node , "nova-compute" , False)

	def novaServiceDown(self, node):
		return NovaClient._helper.services.force_down(node , "nova-compute" , True)

	def liveMigrateVM(self,instanceID,target_host):
		#print ""
		instance = self.getVM(instanceID)
		#print "vm",instance
		#print target_host
		instance.live_migrate(host = target_host)
		time.sleep(60)
		return self.getInstanceHost(instanceID)

	def evacuate(self,vm, failNode, target):
		self.novaServiceDown(failNode)
		NovaClient._helper.servers.evacuate(vm , target , force=True)
		self.novaServiceUp(failNode)



if __name__ == "__main__":
	a = NovaClient.getInstance()
	#print NovaClient().getHypervisorsList()
	#print a.getVM("4df5a97d-9cf2-4d47-99a2-cf68e107acf6")
	#print a.isInstanceExist("4df5a97d-9cf2-4d47-99a2-cf68e107acf6")
	#print a.getInstanceList()[0].isIllegal()
	print a.getAllInstanceList()
	print a.getInstanceListByNode("compute1")