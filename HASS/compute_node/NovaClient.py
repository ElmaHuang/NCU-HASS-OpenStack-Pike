#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import ConfigParser
import time


class NovaClient(object):
    _instance = None  # class reference
    _helper = None  # novaclient reference

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass_node.conf')
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
        auth = v3.Password(auth_url='http://controller:5000/v3',
                           username=self.config.get("openstack", "openstack_admin_account"),
                           password=self.config.get("openstack", "openstack_admin_password"),
                           project_name=self.config.get("openstack", "openstack_project_name"),
                           user_domain_name=self.config.get("openstack", "openstack_user_domain_id"),
                           project_domain_name=self.config.get("openstack", "openstack_project_domain_id"))
        sess = session.Session(auth=auth)
        novaClient = client.Client(2.29, session=sess)
        return novaClient

    def getVM(self, id):
        return NovaClient._helper.servers.get(id)

    def getInstanceState(self, instance_id):
        instance = self.getVM(instance_id)
        return getattr(instance, "status")

    def hardReboot(self, id):
        instance = self.getVM(id)
        NovaClient._helper.servers.reboot(instance, reboot_type='HARD')

    def softReboot(self, id):
        instance = self.getVM(id)
        NovaClient._helper.servers.reboot(instance, reboot_type='SOFT')

    def getAllInstanceList(self):
        return NovaClient._helper.servers.list(search_opts={'all_tenants': 1})

    def getInstanceNetwork(self, instance_id):
        instance = self.getVM(instance_id)
        network = getattr(instance, "networks")
        return network

    def isInstancePowerOn(self, id):
        vm = self.getVM(id)
        power_state = getattr(vm, "OS-EXT-STS:power_state")
        if power_state != 1:
            return False
        return True


if __name__ == "__main__":
    a = NovaClient.getInstance()
    a.hardReboot("219046ce-1c1e-4a73-ac53-4cacafd08e79")
