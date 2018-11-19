#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################
#:Date: 2018/2/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains OpenStack-Nova command operation in computing node
##############################################################


import ConfigParser
import logging

from keystoneauth1 import session
from keystoneauth1.identity import v3
from novaclient import client


class NovaClient(object):
    _instance = None  # class reference
    _helper = None  # novaclient reference

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass_node.conf')
        if NovaClient._instance is not None:
            raise Exception("This class is a singleton! , cannot initialize twice")
        else:
            self.initialize_helper()
            NovaClient._instance = self

    @staticmethod
    def get_instance():
        if not NovaClient._instance:
            NovaClient()
        if not NovaClient._helper:
            NovaClient._instance.initialize_helper()
        return NovaClient._instance

    def initialize_helper(self):
        NovaClient._helper = self.get_helper()

    def get_helper(self):
        auth = v3.Password(auth_url = 'http://controller:5000/v3',
                           username = self.config.get("openstack", "openstack_admin_account"),
                           password = self.config.get("openstack", "openstack_admin_password"),
                           project_name = self.config.get("openstack", "openstack_project_name"),
                           user_domain_name = self.config.get("openstack", "openstack_user_domain_id"),
                           project_domain_name = self.config.get("openstack", "openstack_project_domain_id"))
        sess = session.Session(auth = auth)
        novaClient = client.Client(2.29, session = sess)
        return novaClient

    def get_vm(self, id):
        """

        :param id: 
        :return: 
        """
        return NovaClient._helper.servers.get(id)

    def get_all_instance_list(self):
        """

        :return: 
        """
        return NovaClient._helper.servers.list(search_opts = {'all_tenants': 1})

    def get_instance_state(self, instance_id):
        """

        :param instance_id: 
        :return: 
        """
        try:
            instance = self.get_vm(instance_id)
            return getattr(instance, "status")
        except Exception as e:
            print("get_instance_state--Exception:", str(e))
            return None

    def hard_reboot(self, id):
        """

        :param id: 
        """
        try:
            instance = self.get_vm(id)
            NovaClient._helper.servers.reboot(instance, reboot_type = 'HARD')
            logging.info("hard reboot success--vm id = %s" % id)
        except Exception as e:
            logging.error(str(e))

    def soft_reboot(self, id):
        """

        :param id: 
        """
        try:
            instance = self.get_vm(id)
            NovaClient._helper.servers.reboot(instance, reboot_type = 'SOFT')
            logging.info("soft reboot success--vm id = %s" % id)
        except Exception as e:
            logging.error(str(e))

    def get_instance_external_network(self, ip):
        """

        :param ip: 
        :return: 
        """
        ext_ip = self.config.get("openstack", "openstack_external_network_gateway_ip").split(".")
        ext_ip = ext_ip[0:-1]
        check_ip = ip.split(".")
        if all(x in check_ip for x in ext_ip):
            return ip
        return None

    # def get_all_instance_list(self):
    #     return NovaClient._helper.servers.list(search_opts={'all_tenants': 1})
    #
    # def getInstanceNetwork(self, instance_id):
    #     instance = self.get_vm(instance_id)
    #     network = getattr(instance, "networks")
    #     return network
    #
    # def isInstancePowerOn(self, id):
    #     vm = self.get_vm(id)
    #     power_state = getattr(vm, "OS-EXT-STS:power_state")
    #     if power_state != 1:
    #         return False
    #     return True


if __name__ == "__main__":
    pass
    # a = NovaClient.get_instance()
    # a.hard_reboot("21ffc94c-343e-4813-96b6-5d7d593a6449")
