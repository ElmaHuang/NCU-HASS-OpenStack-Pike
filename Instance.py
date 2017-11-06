from NovaClient import NovaClient
import logging

class Instance(object):

	def __init__(self, id, name, host):
		self.id = id
		self.name = name
		self.host = host
		self.status=None
		self.nova_client = NovaClient.getInstance()

	def isPowerOn(self):
		return self.nova_client.isInstancePowerOn(self.id)

	def hasVolume(self):
		return self.nova_client.isInstanceGetVolume(self.id)
	''''
	def isPowerOn(self):
		if not self.isPowerOn():
			logging.info("VM %s is not running" % self.name)
			return False
		return True
	'''
	def updateInfo(self):
		self.host=self.nova_client.getInstanceHost(self.id) #checkinstanceState ??
		self.status=self.nova_client.getInstanceState(self.id)

	def getInfo(self):
		self.updateInfo()
		return [self.id, self.name, self.host, self.status]