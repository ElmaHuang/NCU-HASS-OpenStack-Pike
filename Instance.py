from NovaClient import NovaClient
import logging

class Instance(object):

	def __init__(self, id, name, host):
		self.id = id
		self.name = name
		self.host = host
		self.nova_client = NovaClient.getInstance()

	def isPowerOn(self):
		return self.nova_client.isInstancePowerOn(self.id)

	def hasVolume(self):
		return self.nova_client.isInstanceGetVolume(self.id)

	def isIllegal(self):	
		if not self.isPowerOn():
			logging.info("VM %s is not running" % self.name)
			return False
		# elif not self.hasVolume():
		# 	logging.info("VM %s is not having volume" % self.name)
		# 	return False
		return True

	def getInfo(self):
		return [self.id , self.name , self.host]