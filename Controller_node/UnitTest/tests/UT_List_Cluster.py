import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"


def run():
    ClusterManager.init()
    ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)

    try:
        result = ClusterManager.listCluster()
        if len(result) >= 1:
            return True
        else:
            return False
    except Exception as e:
        print "UT_List_Cluster Except:" + str(e)
        return False
