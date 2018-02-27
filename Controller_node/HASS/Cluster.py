# ########################################################
# :Date: 2017/12/13
# :Version: 1
# :Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
# :Python_Version: 2.7
# :Platform: Unix
# :Description:
# This is a class which maintains cluster data structure.
# #########################################################

import logging

from ClusterInterface import ClusterInterface
from Instance import Instance
from Node import Node
from Response import Response


class Cluster(ClusterInterface):
    def __init__(self, id, name):
        super(Cluster, self).__init__(id, name)

    def addNode(self, node_name_list):
        # create node list
        message = ""
        result = None
        try:
            for node_name in node_name_list:
                # check node is in computing pool
                if self.nova_client.isInComputePool(node_name):
                    node = Node(name=node_name, cluster_id=self.id)
                    self.node_list.append(node)
                    node.startDetectionThread()
                    message = "Cluster--The node %s is added to cluster." % self.getAllNodeStr()
                    data = {"cluster_id": self.id, "node_list": self.getAllNodeStr()}
                    result = self.successResult(message, data)
                    logging.info(message)
                else:
                    message += "Cluster--The node %s is illegal.  " % node_name
                    logging.error(message)
            # no node be added into node_list
            if result is None:
                data = {"cluster_id": self.id}
                result = self.failResult(message, data)
        except Exception as e:
            message = "Cluster-- add node function fail.%s" % str(e)
            data = {"cluster_id": self.id}
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": self.id})
        finally:
            return result

    def deleteNode(self, node_name):
        result = None
        try:
            node = self.getNodeByName(node_name)
            # stop Thread
            node.deleteDetectionThread()
            self.deleteInstanceByNode(node)
            self.node_list.remove(node)
            message = "Cluster delete node success! node is %s , node list is %s,cluster id is %s." % (
                node_name, self.getAllNodeStr(), self.id)
            data = {"cluster_id": self.id, "node": node_name}
            result = self.successResult(message, data)
            logging.info(message)
            # result = Response(code="succeed",
            #                   message=message,
            #                   data={"cluster_id": self.id, "node": node_name})
        except Exception as e:
            # print str(e)
            message = "Cluster--delete node fail , node maybe not in compute pool please check again! node is %s  The node list is %s.%s" % (
                node_name, self.getAllNodeStr(), str(e))
            data = {"cluster_id": self.id, "node": node_name}
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": self.id, "node": node_name})
        finally:
            return result

    def getAllNodeInfo(self):
        ret = []
        for node in self.node_list:
            ret.append(node.getInfo())
        return ret

    def addInstance(self, instance_id, send_flag=True):
        result = None
        message = ""
        try:
            if not self.checkInstanceExist(instance_id):
                message += "There is no this instance in any node!"
                # raise Exception("There is no this instance in any node!")
            if not self.checkInstanceGetVolume(instance_id):
                message += "The instance don't have volume"
                # raise Exception("The instance don't have volume")
            if not self.checkInstancePowerOn(instance_id):
                message += "This instance is power off!"
                # raise Exception("This instance is power off!")
            if message:
                data = {"cluster_id": self.id, "instance_id": instance_id}
                result = self.failResult(message, data)
                logging.error(message)
            else:
                # Live migration VM to cluster node
                final_host = self.getInstanceHost(instance_id)
                if not final_host:
                    final_host = self.liveMigrateInstance(instance_id)
                instance = Instance(id=instance_id,
                                    name=self.nova_client.getInstanceName(instance_id),
                                    host=final_host,
                                    status=self.nova_client.getInstanceState(instance_id),
                                    network=self.nova_client.getInstanceNetwork(instance_id))
                if send_flag:
                    self.sendUpdateInstance(final_host)
                self.instance_list.append(instance)
                message = "Cluster--Cluster add instance success ! The instance id is %s." % instance_id
                data = {"cluster_id": self.id, "node": final_host, "instance_id": instance_id}
                result = self.successResult(message, data)
                logging.info(message)
                # result = Response(code="succeed",
                #                   message=message,
                #                   data={"cluster_id": self.id, "node": final_host, "instance_id": instance_id})
        except Exception as e:
            message = "Cluster--Cluster add instance fail ,please check again! The instance id is %s. %s" % (
                instance_id, str(e))
            data = {"cluster_id": self.id, "instance_id": instance_id}
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": self.id, "instance_id": instance_id})
        finally:
            return result

    def deleteInstance(self, instance_id, send_flag=True):
        result = None
        try:
            # find instance in instance_list
            for instance in self.instance_list:
                prev_host = instance.host
                if instance.id == instance_id:
                    self.instance_list.remove(instance)
                    if send_flag:
                        self.sendUpdateInstance(prev_host)
                    message = "Cluster--delete instance success. this instance is deleted (instance_id = %s)" % instance_id
                    data = {"cluster_id": self.id, "instance_id": instance_id}
                    result = self.successResult(message, data)
                    logging.info(message)
                    # result = Response(code="succeed",
                    #                   message=message,
                    #                   data={"cluster_id": self.id, "instance_id": instance_id})

            # if instance id not in self.instance_list:
            if result is None:
                message = "Cluster--delete instance fail. maybe this instance is not in instance_list(instance_id = %s)" % instance_id
                data = {"cluster_id": self.id, "instance_id": instance_id}
                result = self.failResult(message, data)
                logging.error(message)
                # result = Response(code="failed",
                #                   message=message,
                #                   data={"cluster_id": self.id, "instance_id": instance_id})
        except Exception as e:
            message = "Cluster--delete instance fail . The instance id is %s.%s" % (instance_id, str(e))
            data = {"cluster_id": self.id, "instance_id": instance_id}
            result = self.failResult(message, data)
            logging.error(message)
            # result = {"code": "1", "cluster id": self.id, "instance id": instance_id, "message": message}
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": self.id, "instance_id": instance_id})
        finally:
            return result

    def deleteInstanceByNode(self, node):
        protected_instance_list = self.getProtectedInstanceListByNode(node)
        for instance in protected_instance_list:
            self.deleteInstance(instance.id, send_flag=False)
        self.sendUpdateInstance(node.name)

    # list Instance
    def getAllInstanceInfo(self):
        instance_info = []
        try:
            for instance in self.instance_list[:]:
                # prev_host = instance.host
                # check_instance_result = self._checkInstance(instance)
                # if check_instance_result == False:
                #   illegal_instance.append((instance.id, prev_host))
                # else:
                info = instance.getInfo()
                instance_info.append(info)
        except Exception as e:
            message = "cluster--getAllInstanceInfo fail:" + str(e)
            logging.error(message)
        finally:
            # return legal_instance, illegal_instance
            return instance_info

    def _checkInstance(self, instance):
        try:
            instance_info = instance.getInfo()
            host = instance_info[2]
            if "SHUTOFF" in instance_info:
                return False
            elif host not in self.getAllNodeStr():
                return False
            else:
                return True
        except Exception as e:
            print "Cluster--_checkInstance-exception--" + str(e)
            return False

    # cluster.addInstance
    def findNodeByInstance(self, instance_id):
        for node in self.node_list:
            if node.containsInstance(instance_id):
                return node
        return None

    # def _isInComputePool(self, unchecked_node_name):
    #     return unchecked_node_name in self.nova_client.getComputePool()

    # be DB called
    def getNodeList(self):
        return self.node_list

    def sendUpdateInstance(self, host_name):
        print "send mesg to ", host_name
        host = self.getNodeByName(host_name)
        if host is None:
            print "%s is not in cluster" % host_name
        else:
            result = host.sendUpdateInstance()
            if not result:
                print "%s host send update instance mesg fail" % host_name

    # be deleteNode/RecoveryManager called
    def getNodeByName(self, name):
        # node_list = self.getNodeList()
        for node in self.node_list:
            if node.name == name:
                return node
        return None

    # addNode message
    def getAllNodeStr(self):
        ret = ""
        for node in self.node_list:
            ret += node.name + " "
        return ret

    # clustermanager.deletecluster call
    def deleteAllNode(self):
        for node in self.node_list[:]:
            self.deleteNode(node.name)
            # print "node list:",self.node_list

    def getClusterInfo(self):
        return [self.id, self.name]

    def checkInstanceGetVolume(self, instance_id):
        if not self.nova_client.isInstanceGetVolume(instance_id):
            message = "this instance not having volume! Instance id is %s " % instance_id
            logging.error(message)
            return False
        return True

    def checkInstancePowerOn(self, instance_id):
        if not self.nova_client.isInstancePowerOn(instance_id):
            message = "this instance is not running! Instance id is %s " % instance_id
            logging.error(message)
            return False
        return True

    def checkInstanceExist(self, instance_id):
        # node_list = self.nova_client.getComputePool()
        # print "node list of all compute node:", node_list
        instance_list = self.nova_client.getAllInstanceList()
        # print instance_list
        for instance in instance_list:
            if instance.id == instance_id:
                logging.info("Cluster--addInstance-checkInstanceExist success")
                return True
        logging.error("this instance is not exist. Instance id is %s. " % instance_id)
        return False

    def isProtected(self, instance_id):
        for instance in self.instance_list[:]:
            if instance.id == instance_id:
                return True
        message = "this instance is  already in the cluster. Instance id is %s. cluster id is %s .instance list is %s" % (
            instance_id, self.id, self.instance_list)
        logging.error(message)
        return False

    def isInstanceInCluster(self, instance):
        node_list = self.getNodeList()
        if instance.host in node_list:
            return True
        return False

    def findTargetHost(self, fail_node):
        import random
        target_list = [node for node in self.node_list if node != fail_node]
        target_host = random.choice(target_list)
        return target_host

    def updateInstance(self):
        for instance in self.instance_list:
            instance.updateInfo()
            # if instance not in cluster, delete the instance
            if not self.isInstanceInCluster(instance):
                self.deleteInstance(instance.id, send_flag=True)
            print "instance %s update host to %s" % (instance.name, instance.host)
            # instance.host = host

    def getInstanceHost(self, instance_id):
        host = self.nova_client.getInstanceHost(instance_id)
        for node in self.node_list[:]:
            if host == node.name:
                return host
        return None

    def liveMigrateInstance(self, instance_id):
        host = self.nova_client.getInstanceHost(instance_id)
        target_host = self.findTargetHost(host)
        print "start live migrate vm from ", host, "to ", target_host.name
        final_host = self.nova_client.liveMigrateVM(instance_id, target_host.name)
        return final_host

    def evacuate(self, instance, target_host, fail_node):
        self.nova_client.evacuate(instance, target_host, fail_node)

    def getProtectedInstanceList(self):
        return self.instance_list

    def getProtectedInstanceListByNode(self, node):
        ret = []
        # protected_instance_list = self.getProtectedInstanceList()
        for instance in self.instance_list:
            if instance.host == node.name:
                ret.append(instance)
        return ret

    def successResult(self, message, data):
        result = Response(code="succeed",
                          message=message,
                          data=data)
        return result

    def failResult(self, message, data):
        result = Response(code="failed",
                          message=message,
                          data=data)
        return result


if __name__ == "__main__":
    a = Cluster("123", "name")
    list = ["compute3"]
    a.addNode(list)
    # host = a.findNodeByInstance("0e0ce568-4ae3-4ade-b072-74edeb3ae58c")
    # print "h:",host

    '''
    def _isNodeDuplicate(self , unchecked_node_name):
        for node in self.node_list:
            if node.name == unchecked_node_name:
                return True
        return False

    #addNode call
    def _getIPMIStatus(self, node_name):
        config = ConfigParser.RawConfigParser()
        config.read('hass.conf')
        ip_dict = dict(config._sections['ipmi'])
        return node_name in ip_dict

    def _nodeIsIllegal(self , unchecked_node_name):
        if not self._isInComputePool(unchecked_node_name):
            return True
        #if self._isNodeDuplicate(unchecked_node_name):
            #return True
        return False		
    '''
