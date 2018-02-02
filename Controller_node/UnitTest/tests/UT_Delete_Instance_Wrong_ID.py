import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager
import Preprocess, Postprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2"]


def run():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False, send_flag=False)

    wrong_instance_id = "wrong id"
    try:
        result = ClusterManager.deleteInstance(cluster_id, wrong_instance_id, write_DB=False, send_flag=False)
        print result
        if result.code == "failed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Delete_Instance_Wrong_ID Except:" + str(e)
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, NODE_NAME[0], write_DB=False)
        Postprocess.deleteInstance()
