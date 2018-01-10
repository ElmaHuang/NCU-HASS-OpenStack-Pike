import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute6"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)["clusterId"]
    try:
        result = ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        if result["code"] == "0":
            return False
        else:
            return True
    except:
        return True
