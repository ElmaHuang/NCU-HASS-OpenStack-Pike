import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)["clusterId"]
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)

    wrong_cluster_id = "wrong id"
    try:
        result = ClusterManager.listNode(wrong_cluster_id)
        if len(result["nodeList"]) == 1:
            return False
    except:
        return True
    finally:
        ClusterManager.deleteNode(cluster_id, "compute1", write_DB=False)
