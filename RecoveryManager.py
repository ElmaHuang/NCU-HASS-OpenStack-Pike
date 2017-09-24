#!/usr/bin/python
"""
Create/Delete/List cluster, node and instance.
Using openstack API to communicate with openstack
"""
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import logging
import ConfigParser
import time
import subprocess
import paramiko
import socket


from Cluster import Cluster   # cluster data structure pseudo
from DatabaseManager import DatabaseManager
from IPMIModule import IPMIManager
ipmi_manager = IPMIManager()

class RecoveryManager (object):

    def __init__ (self, system_test = False,  test=False):
        pass

def main():
   pass

if __name__ == "__main__":
    main()
