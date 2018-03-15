#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains Openstack-Nova command operation
##############################################################

# from ClusterManager import ClusterManager
import ConfigParser
import logging
import time

from keystoneauth1 import session
from keystoneauth1.identity import v3
from novaclient import client


class NovaClient(object):
    _instance = None  # class reference
    _helper = None  # novaclient reference

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.version = self.config.get("version", "version")
        if NovaClient._instance is not None:
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
        if self.version == "16":
            novaClient = client.Client(2.29, session=sess)
        else:
            novaClient = client.Client(2.25, session=sess)
        return novaClient

    def getComputePool(self):
        compute_pool = []
        hypervisor_list = self._getHostList()
        for hypervisor in hypervisor_list:
            compute_pool.append(str(hypervisor.hypervisor_hostname))
        return compute_pool

    def isInComputePool(self, name):
        return name in self.getComputePool()

    def _getHostList(self):
        return NovaClient._helper.hypervisors.list()

    def getVM(self, id):
        # vm = None
        try:
            vm = NovaClient._helper.servers.get(id)
            return vm
        except Exception as e:
            print "novaclient--getvm-exception:", str(e)

    def getInstanceState(self, instance_id):
        instance = self.getVM(instance_id)
        # if instance == None:return None
        return getattr(instance, "status")

    def getAllInstanceList(self):
        return NovaClient._helper.servers.list(search_opts={'all_tenants': 1})

    def getInstanceName(self, instance_id):
        instance = self.getVM(instance_id)
        # if instance == None:return None
        return getattr(instance, "OS-EXT-SRV-ATTR:instance_name")

    def checkInstanceStatus(self, instance_id, check_timeout=60):
        status = None
        instance = self.getVM(instance_id)
        while status != "ACTIVE" and check_timeout > 0:
            status = self.getInstanceState(instance_id)
            print "checkInstanceStatus in nova-client : %s , %s" % (status, getattr(instance, "name"))
            check_timeout -= 1
            time.sleep(1)
        # timeout
        if status != "ACTIVE":
            message = "NovaClient checkInstanceStatus fail,time out and state is not ACTIVE.instance_id = %s" % instance_id
            print message
            logging.error(message)
            return False
        return True

    def getInstanceHost(self, instance_id):
        instance = self.getVM(instance_id)
        return getattr(instance, "OS-EXT-SRV-ATTR:host")

    def getInstanceNetwork(self, instance_id):
        instance = self.getVM(instance_id)
        network = getattr(instance, "networks")
        return network

    def getInstanceExternalNetwork(self, ip):
        ext_ip = self.config.get("openstack", "openstack_external_network_gateway_ip").split(".")
        ext_ip = ext_ip[0:-1]
        check_ip = ip.split(".")
        if all(x in check_ip for x in ext_ip):
            return ip
        return None

    def isInstancePowerOn(self, id):
        vm = self.getVM(id)
        power_state = getattr(vm, "OS-EXT-STS:power_state")
        if power_state != 1:
            return False
        return True

    def getVolumes(self, id):
        return NovaClient._helper.volumes.get_server_volumes(id)

    def isInstanceGetVolume(self, id):
        volume = self.getVolumes(id)
        if not volume:
            return False
        return True

    def novaServiceUp(self, node):
        return NovaClient._helper.services.force_down(node.name, "nova-compute", False)

    def novaServiceDown(self, node):
        return NovaClient._helper.services.force_down(node.name, "nova-compute", True)

    def liveMigrateVM(self, instance_id, target_host):
        try:
            instance = self.getVM(instance_id)
            instance.live_migrate(host=target_host)
            status = self.checkInstanceStatus(instance_id)
            if status:
                return self.getInstanceHost(instance_id)
            raise Exception("Instance Status is not ACTIVE .instance id = %s" % instance_id)
        except Exception as e:
            message = "NovaClient live migration fail" + str(e)
            logging.error(message)

    def evacuate(self, instance, target_host, fail_node):
        try:
            self.novaServiceDown(fail_node)
            openstack_instance = self.getVM(instance.id)
            if self.version == "16":
                NovaClient._helper.servers.evacuate(openstack_instance, target_host.name, force=True)
            else:
                NovaClient._helper.servers.evacuate(openstack_instance, target_host.name)
            self.novaServiceUp(fail_node)
            status = self.checkInstanceStatus(instance.id)
            if status:
                return self.getInstanceHost(instance.id)
            raise Exception("Instance Status is not ACTIVE .instance id = %s" % instance.id)
        except Exception as e:
            message = "NovaClient evacuate fail" + str(e)
            logging.error(message)


if __name__ == "__main__":
    a = NovaClient.getInstance()
    '''
    def getInstanceListByNode(self, node_name):
        ret = []
        instance_list = self.getAllInstanceList()
        for instance in instance_list:
            name = getattr(instance, "OS-EXT-SRV-ATTR:hypervisor_hostname")
            if name == node_name:
                ret.append(instance)
        return ret
        
    def isInstanceExist(self, instance_id):
        try:
            NovaClient._helper.servers.get(instance_id)
            return True
        except Exception as e:
            message = "NovaClient isInstanceExist get instance fail" + str(e)
            logging.error(message)
            return False
    '''
