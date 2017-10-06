from NovaClient import NovaClient
import logging

class Instance(object):

	def __init__(self, id, name, host):
		self.id = id
		self.name = name
		self.host = host

	def getInfo(self):
		return [self.id , self.name , self.host]