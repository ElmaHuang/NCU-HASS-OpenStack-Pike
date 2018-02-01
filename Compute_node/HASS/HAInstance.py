import subprocess

from Instance import Instance
from RPCServer import RPCServer


class HAInstance():
    server = RPCServer.getRPCServer()
    instance_list = None
    ha_instance_list = None
    host = subprocess.check_output(['hostname']).strip()

    @staticmethod
    def init():
        HAInstance.instance_list = []
        HAInstance.ha_instance_list = {}

    @staticmethod
    def getInstanceFromController():
        host_instance = {}
        try:
            cluster_list = HAInstance.server.listCluster()
            for cluster in cluster_list:
                cluster_uuid = cluster[0]
                HAInstance.ha_instance_list[cluster_uuid] = HAInstance._getHAInstance(cluster_uuid)
                # for clusteruuid,ha_instance_list in ha_instance_list.iter:, width=1)
            host_instance = HAInstance._getInstanceByNode(HAInstance.ha_instance_list)
            for cluster_id, instance_list in host_instance.iteritems():
                for instance in instance_list:
                    # print cluster_id
                    # print instance
                    HAInstance.addInstance(cluster_id, instance)
            # return host_instance
        except Exception as e:
            print "getInstanceFromController-e:", str(e)

    @staticmethod
    def _getHAInstance(clusterId):
        instance_list = []
        try:
            instance_list = HAInstance.server.listInstance(clusterId, False)["data"]["instance_list"]
        except Exception as e:
            print "get ha instance fail" + str(e)
            # instance_list = []
        finally:
            return instance_list

    @staticmethod
    def _getInstanceByNode(instance_lists):
        for id, instance_list in instance_lists.iteritems():
            for instance in instance_list[:]:
                if HAInstance.host not in instance[2]:
                    print instance[2]
                    instance_list.remove(instance)
        return instance_lists

    @staticmethod
    def addInstance(cluster_id, instance):
        print "add vm"
        vm = Instance(cluster_id=cluster_id, ha_instance=instance)
        HAInstance.instance_list.append(vm)

    @staticmethod
    def getInstanceList():
        return HAInstance.instance_list

    @staticmethod
    def getInstance(name):
        for instance in HAInstance.instance_list:
            if instance.name == name:
                return instance
