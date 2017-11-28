from NovaClient import NovaClient
import logging
import socket

class Instance(object):

	def __init__(self, id, name, host, status, network):
		self.id = id
		self.name = name
		self.host = host
		self.network = None
		self.status=None
		self.nova_client = NovaClient.getInstance()
		self.updateInfo()
		#self.sendIP()

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
		self.host = self.nova_client.getInstanceHost(self.id) #checkinstanceState ??
		self.status = self.nova_client.getInstanceState(self.id)
		self.network = self.nova_client.getInstanceNetwork(self.id)

	def getInfo(self):
		self.updateInfo()
		return [self.id, self.name, self.host, self.status,self.network]
	'''
	def sendUpdate(self):
		so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		so.connect((self.host ,5001))
		#ip = so.recv(1024)
		so.send(str(self.network))
		#print ip
		so.close()

	def sendDeleteIP(self):
		so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		so.connect((self.host, 5001))
		# ip = so.recv(1024)
		so.send()
		# print ip
		so.close()
	'''