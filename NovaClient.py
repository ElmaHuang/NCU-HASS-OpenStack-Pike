#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import ConfigParser

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
		hypervisorList = self._getHypervisorsList()
		for hypervisor in hypervisorList:
			computePool.append(str(hypervisor.hypervisor_hostname))
		return computePool

	def _getHypervisorsList(self):
		return NovaClient._helper.hypervisors.list()

	def getVM(id):
		return NovaClient._helper.servers.get(id)

	def getVolumes(id):
		return NovaClient._helper.volumes.get_server_volumes(id)

	def novaServiceUp(node):
		return NovaClient._helper.services.force_down(node , "nova-compute" , False)

	def novaServiceDown(node):
		return NovaClient._helper.services.force_down(node , "nova-compute" , True)

	def evacuate(vm , failNode , target):
		self.novaServiceDown(failNode)
		NovaClient._helper.servers.evacuate(vm , target , force=True)
		self.novaServiceUp(failNode)



if __name__ == "__main__":
	a = NovaClient.getInstance()
	#print NovaClient().getHypervisorsList()

	print a.getComputePool()