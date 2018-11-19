import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2"]
WRONG_INSTANCE_ID = "wrong-id"


def run():
    ClusterManager.init()
    cluster = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)

    try:
        result = ClusterManager.addInstance(cluster_id, WRONG_INSTANCE_ID, write_DB=False, send_flag=False)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_Add_Wrong_Instance Except:" + str(e)
        return False
