import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"


def run():
    ClusterManager.init()
    ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = "wrong"
    try:
        result = ClusterManager.deleteCluster(cluster_id)
        if result.code == "failed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Delete_Wrong_Cluster Except:" + str(e)
        return False
