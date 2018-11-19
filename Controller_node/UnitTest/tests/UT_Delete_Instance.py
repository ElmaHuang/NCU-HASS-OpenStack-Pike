import sys

import Postprocess
import Preprocess

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2"]


def run():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False, send_flag=False)
    try:
        result = ClusterManager.deleteInstance(cluster_id, instance_id, write_DB=False, send_flag=False)
        if result.code == "succeed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Delete_Instance Except:" + str(e)
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, NODE_NAME[0], write_DB=False)
        Postprocess.deleteInstance()
