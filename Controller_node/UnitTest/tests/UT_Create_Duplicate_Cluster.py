import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"


def run():
    try:
        ClusterManager.init()
        result = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
        if result.code == "succeed":
            dup_result = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
            if dup_result.code == "succeed":
                return False
            else:
                return True
        else:
            return False
    except Exception as e:
        print "UT_Create_Duplicate_Cluster Except:" + str(e)
        return False
