import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute6"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    try:
        result = ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_Add_Wrong_Node Except:" + str(e)
        return False
