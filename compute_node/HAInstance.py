
import ConfigParser
import xmlrpclib
import subprocess
from Instance import Instance

from RESTClient import RESTClient

class HAInstance():
    instance_list = None
    HA_instance_list = None
    server = RESTClient.getInstance()

    @staticmethod
    def init():
        HAInstance.instance_list = []
        HAInstance.HA_instance_list = {}

    @staticmethod
    def addInstance(ha_instance):
        id = ha_instance.id
        HAInstance.HA_instance_list[id] = ha_instance
        print len(HAInstance.HA_instance_list)

    @staticmethod
    def getInstanceList():
        return HAInstance.HA_instance_list

    @staticmethod
    def getInstance(name):
        for id, instance in HAInstance.HA_instance_list.iteritems():
            if instance.name == name:
                return instance

    @staticmethod
    def updateHAInstance():
        # self.clearlog()
        HAInstance.init()
        instance_list = HAInstance.getInstanceFromController()
        for instance in instance_list[:]:
            # [self.id, self.name, self.host, self.status, self.network]
            vm = Instance(ha_instance=instance)
            HAInstance.addInstance(vm)
        print HAInstance.HA_instance_list
            # self.writelog(ha_vm)

    @staticmethod
    def getInstanceFromController():
        host_instance = []
        cluster_list = HAInstance.server.list_cluster()["data"]
        for cluster in cluster_list:
            clusterId = cluster["cluster_id"]
            instance_list = HAInstance._getHAInstance(clusterId)
            print "HA instacne list:", instance_list
            host_instance = HAInstance._getInstanceByNode(instance_list)
        return host_instance

    @staticmethod
    def _getHAInstance(clusterId):
        try:
            instance_list = HAInstance.server.list_instance(clusterId)["data"]["instanceList"]
        except Exception as e:
            print "get ha instance fail" + str(e)
            instance_list = []
        finally:
            return instance_list

    @staticmethod
    def _getInstanceByNode(instance_list):
        host_instance = []
        host = subprocess.check_output(['hostname']).strip()
        for instance in instance_list:
            if host in instance["host"]:
                host_instance.append(instance)
        return host_instance
