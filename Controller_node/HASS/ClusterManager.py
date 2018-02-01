#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#	This is a static class which maintains all the data structure.
##########################################################
import logging
import uuid

from Cluster import Cluster
from DatabaseManager import DatabaseManager
from NovaClient import NovaClient
from Response import Response


class ClusterManager():
    _cluster_dict = None
    _db = None
    _RESET_DB = False
    nova = NovaClient.getInstance()

    @staticmethod
    def init():
        ClusterManager._cluster_dict = {}
        ClusterManager._db = DatabaseManager()
        ClusterManager._db.createTable()
        ClusterManager.syncFromDatabase()

    @staticmethod
    def createCluster(cluster_name, cluster_id=None, write_DB=True):
        if ClusterManager._isNameOverLapping(cluster_name):
            message = "ClusterManager - cluster name overlapping"
            data = {"cluster_id": cluster_id}
            result = ClusterManager.failResult(message, data)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        else:
            logging.info("ClusterManager - cluster name is not overlapping")
            result = ClusterManager._addToClusterList(cluster_name, cluster_id)
            if result.code == "succeed" and write_DB:
                ClusterManager.syncToDatabase()
        return result

    @staticmethod
    def deleteCluster(cluster_id, write_DB=True):
        result = None
        message = ""
        data = {"cluster_id": cluster_id}
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "The cluster is not found. (cluster_id = %s)" % cluster_id
                result = ClusterManager.failResult(message, data)
                # result = Response(code="failed",
                #                   message=message,
                #                   data={"cluster_id": cluster_id})
            else:
                cluster.deleteAllNode()
                # check delete all nodes of cluster
                if not cluster.node_list:
                    del ClusterManager._cluster_dict[cluster_id]
                else:
                    message = "Delete all nodes of cluster fail"
                    logging.error(message)
                    result = ClusterManager.failResult(message, data)
                    # result = Response(code="failed",
                    #                   message=message,
                    #                   data={"clusterId": cluster_id})
                if result is None:
                    message = "Delete cluster success. The cluster is deleted. (cluster_id = %s)" % cluster_id
                    result = ClusterManager.successResult(message, data)
                    logging.info(message)
                    # result = Response(code="succeed",
                    #                   message=message,
                    #                   data={"cluster_id": cluster_id})
                if result.code == "succeed" and write_DB:
                    ClusterManager.syncToDatabase()
        except Exception as e:
            message += "ClusterManager--deleteCluster fail" + str(e)
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def getClusterList():
        return ClusterManager._cluster_dict

    @staticmethod
    def listCluster():
        res = []
        for id, cluster in ClusterManager._cluster_dict.iteritems():
            res.append((cluster.getClusterInfo()))
        return res

    @staticmethod
    def addNode(cluster_id, node_name_list, write_DB=True):
        result = None
        data = {"cluster_id": cluster_id}
        message = ""
        try:
            # delete illegal node
            tmp_list = node_name_list[:]
            for node_name in tmp_list:
                if not ClusterManager._checkNodeOverlappingForAllCluster(node_name):
                    print "%s is already in a HA cluster. " % node_name
                    message += "%s is overlapping node" % node_name
                    tmp_list.remove(node_name)
            # check node list
            if not tmp_list:
                message = "All node(s) in node list are(is) illegal"
                result = ClusterManager.failResult(message, data)
                logging.error(message)
            # node list is not empty
            else:
                cluster = ClusterManager.getCluster(cluster_id)
                if not cluster:
                    message += "ClusterManager--Add the node to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
                    result = ClusterManager.failResult(message, data)
                    # result = Response(code="failed",
                    #                   message=message,
                    #                   data={"cluster_id": cluster_id})
                else:
                    result = cluster.addNode(tmp_list)
                    logging.info(
                        "ClusterManager--add node finish.cluster id is %s ,node is %s " % (cluster_id, tmp_list))
                    if result.code == "succeed" and write_DB:
                        ClusterManager.syncToDatabase()
        except Exception as e:
            message += "add node fail. node not found. (node_name = %s).%s" % (tmp_list, str(e))
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def deleteNode(cluster_id, node_name, write_DB=True):
        result = None
        data = {"cluster_id": cluster_id}
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "delete the node failed. The cluster is not found. (cluster_id = %s)" % cluster_id
                result = ClusterManager.failResult(message, data)
                logging.error(message)
                # result = Response(code="failed",
                #               message=message,
                #               data={"cluster_id": cluster_id})
            else:
                result = cluster.deleteNode(node_name)
                if result.code == "succeed" and write_DB:
                    ClusterManager.syncToDatabase()
                logging.info(
                    "ClusterManager-- delete node finish,cluster id is %s node is %s" % (cluster_id, node_name))
        except Exception as e:
            message = "delete node fail. node not found. (node_name = %s).%s" % (node_name, str(e))
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def listNode(cluster_id):
        result = None
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "ClusterManager--Add the instance to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
                data = {"cluster_id": cluster_id}
                result = ClusterManager.failResult(message, data)
            else:
                node_list = cluster.getAllNodeInfo()
                message = "ClusterManager-listNode--get all node info finish"
                data = {"cluster_id": cluster_id, "node_list": node_list}
                result = ClusterManager.successResult(message, data)
                logging.info(message)
            # result = Response(code="succeed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id, "node_list": node_list})
        except Exception as e:
            message = "ClusterManager--listNode-- get all node info fail. " + str(e)
            data = {"cluster_id": cluster_id}
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def addInstance(cluster_id, instance_id, send_flag=True, write_DB=True):
        result = None
        data = {"cluster_id": cluster_id}
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "ClusterManager--Add the instance to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
                result = ClusterManager.failResult(message, data)
                # result = Response(code="failed",
                #                   message=message,
                #                   data={"cluster_id": cluster_id})
                # return result
            else:
                if not ClusterManager._checkInstanceNOTOverlappingForAllCluster(instance_id):
                    message = "instance already being protected "
                    result = ClusterManager.failResult(message, data)
                else:
                    result = cluster.addInstance(instance_id, send_flag)
                if result.code == "succeed" and write_DB:
                    ClusterManager.syncToDatabase()
                logging.info("ClusterManager--Add instance finish, instance_id : %s , cluster_id : %s" % (
                    instance_id, cluster_id))
        except Exception as e:
            message = "ClusterManager --add the instacne fail.instance_id : %s , cluster_id : %s.%s" % (
                instance_id, cluster_id, str(e))
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def deleteInstance(cluster_id, instance_id, send_flag=True, write_DB=True):
        result = None
        data = {"cluster_id": cluster_id, "instance_id": instance_id}
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "delete the instance to cluster failed. The cluster is not found. (cluster_id = %s)" % cluster_id
                result = ClusterManager.failResult(message, data)
                # result = Response(code="failed",
                #                   message=message,
                #                   data={"cluster_id": cluster_id, "instance_id": instance_id})
            else:
                result = cluster.deleteInstance(instance_id, send_flag)
                if result.code == "succeed" and write_DB:
                    ClusterManager.syncToDatabase()
                logging.info("ClusterManager--delete instance finish")
        except Exception as e:
            message = "ClusterManager--delete instance failed. this instance is not being protected (instance_id = %s),%s" % (
                instance_id, str(e))
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id, "instance_id": instance_id})
        finally:
            return result

    @staticmethod
    def listInstance(cluster_id, send_flag=True):
        result = None
        data = {"cluster_id": cluster_id}
        try:
            cluster = ClusterManager.getCluster(cluster_id)
            if not cluster:
                message = "ClusterManager--listInstance,get instance list fail , not find the cluster %s" % cluster_id
                result = ClusterManager.failResult(message, data)
            else:
                instance_list = cluster.getAllInstanceInfo()
                # delete illegal instance
                # if illegal_instance:
                #     for instance in illegal_instance:
                #         ClusterManager.deleteInstance(cluster_id, instance[0], send_flag=False)
                # send update host of legal instance and prev_host of illegal instance
                # if send_flag:
                #     for instance in instance_list[:]:
                #         cluster.sendUpdateInstance(instance[2])  # info[2]
                #     for instance in illegal_instance[:]:
                #         cluster.sendUpdateInstance(instance[1])  # prev_host
                message = "ClusterManager--listInstance,getInstanceList success,instanceList is %s" % instance_list
                data["instance_list"] = instance_list
                result = ClusterManager.successResult(message, data)
                logging.info(message)
                # result = Response(code="succeed",
                #                   message=message,
                #                   data={"instance_list": instance_list})
        except Exception as e:
            message = "ClusterManager--listInstance,getInstanceList fail" + str(e)
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"instance_list": []})
        finally:
            return result

    @staticmethod
    def _addToClusterList(cluster_name, cluster_id=None):
        result = None
        try:
            if cluster_id:
                cluster = Cluster(id=cluster_id, name=cluster_name)
                ClusterManager._cluster_dict[cluster_id] = cluster
                message = "ClusterManager -syncofromDB-- createCluster._addToCluster success,cluster id = %s" % cluster_id
                data = {"cluster_id": cluster_id}
                result = ClusterManager.successResult(message, data)
                logging.info(message)
                # result = Response(code="succeed",
                #                   message=message,
                #                   data={"cluster_id": cluster_id})
            else:
                # create a new cluster
                cluster_id = str(uuid.uuid4())
                data = {"cluster_id": cluster_id}
                cluster = Cluster(id=cluster_id, name=cluster_name)
                ClusterManager._cluster_dict[cluster_id] = cluster
                message = "ClusterManager - createCluster._addToClusterList success,cluster id = %s" % cluster_id
                result = ClusterManager.successResult(message, data)
                logging.info(message)
                # result = Response(code="succeed",
                #                   message=message,
                #                   data={"cluster_id": cluster_id})
        except Exception as e:
            message = "ClusterManager - createCluster._addToCluster fail,cluster id = %s.%s" % (cluster_id, str(e))
            result = ClusterManager.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed",
            #                   message=message,
            #                   data={"cluster_id": cluster_id})
        finally:
            return result

    @staticmethod
    def _checkNodeOverlappingForAllCluster(node_name):
        for id, cluster in ClusterManager._cluster_dict.items():
            for node in cluster.node_list[:]:
                if node_name == node.name:
                    logging.error("%s already be add into cluster %s" % (node_name, id))
                    return False
        return True

    @staticmethod
    def _checkInstanceNOTOverlappingForAllCluster(instance_id):
        for id, cluster in ClusterManager._cluster_dict.items():
            for instance in cluster.instance_list:
                if instance_id == instance.id:
                    return False
        return True

    @staticmethod
    def getCluster(cluster_id):
        if not ClusterManager._isCluster(cluster_id):
            logging.error("cluster not found id %s" % cluster_id)
            return None
        return ClusterManager._cluster_dict[cluster_id]

    @staticmethod
    def _isNameOverLapping(name):
        for cluster_id, cluster in ClusterManager._cluster_dict.items():
            if cluster.name == name:
                return True
        return False

    @staticmethod
    def _isCluster(cluster_id):
        if cluster_id in ClusterManager._cluster_dict:
            return True
        return False

    @staticmethod
    def reset():
        if ClusterManager._RESET_DB:
            ClusterManager._db.resetAll()
        ClusterManager._cluster_dict = {}
        logging.info("ClusterManager--reset DB ,reset_DB = %s" % ClusterManager._RESET_DB)

    @staticmethod
    def updateAllCluster():
        for cluster_id, cluster in ClusterManager._cluster_dict.items():
            cluster.updateInstance()
        ClusterManager.syncToDatabase()

    @staticmethod
    def syncFromDatabase():
        try:
            ClusterManager.reset()
            exist_cluster = ClusterManager._db.syncFromDB()
            for cluster in exist_cluster:
                ClusterManager.createCluster(cluster["cluster_name"], cluster["cluster_id"], write_DB=False)
                if cluster["node_list"]:
                    ClusterManager.addNode(cluster["cluster_id"], cluster["node_list"], write_DB=False)
                for instance in cluster["instance_list"]:
                    ClusterManager.addInstance(cluster["cluster_id"], instance)
            logging.info("ClusterManager--synco from DB finish")
        except Exception as e:
            logging.error("ClusterManagwer--synco from DB fail.%s" % str(e))

    @staticmethod
    def syncToDatabase():
        cluster_list = ClusterManager._cluster_dict
        ClusterManager._db.syncToDB(cluster_list)

    @staticmethod
    def successResult(message, data):
        result = Response(code="succeed",
                          message=message,
                          data=data)
        return result

    @staticmethod
    def failResult(message, data):
        result = Response(code="failed",
                          message=message,
                          data=data)
        return result


if __name__ == "__main__":
    ClusterManager.init()
    ClusterManager.deleteCluster("8c46ecee-9bd6-4c82-b7c8-6b6d20dc09d7")
