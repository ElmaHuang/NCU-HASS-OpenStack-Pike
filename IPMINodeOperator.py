#!/usr/bin/python
# -*- coding: utf-8 -*-

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import time


class Operator(object):
	def __init__(self):
		# self.clusterList =
		pass

	def startNode(self,node_name):
		pass

	def shutOffNode(self,node_name):
		pass

	def rebootNode(self,node_name):
		pass

	def getTempInfoByNode(self,node_name):
		pass

	def getNodeInfoByType(self,node_name,sensor_type):
		pass


def main():
	pass


if __name__ == '__main__':
	main()