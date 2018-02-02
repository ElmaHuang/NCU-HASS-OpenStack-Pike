import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2"]
WRONG_NODE_NAME = ["compute5"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    try:
        result = ClusterManager.deleteNode(cluster_id, WRONG_NODE_NAME[0], write_DB=False)
        if result.code == "failed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Delete_Wrong_Node_Name Except:" + str(e)
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, NODE_NAME[0], write_DB=False)
