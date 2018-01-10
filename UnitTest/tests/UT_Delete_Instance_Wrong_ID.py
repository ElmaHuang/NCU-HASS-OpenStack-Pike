import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager
import Preprocess
import Postprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)["clusterId"]
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False)

    wrong_instance_id = "wrong id"
    try:
        result = ClusterManager.deleteInstance(cluster_id, wrong_instance_id, write_DB=False)
        print result
        if result["code"] == "0":
            return True
        else:
            return False
    except Exception as e:
        print str(e)
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
        Postprocess.deleteInstance()
