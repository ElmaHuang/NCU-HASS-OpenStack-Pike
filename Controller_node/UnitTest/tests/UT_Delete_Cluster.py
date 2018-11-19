import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"


def run():
    ClusterManager.init()
    cluster_result = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_result.data.get("cluster_id")
    print cluster_id
    try:
        result = ClusterManager.deleteCluster(cluster_id)
        if result.code == "succeed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Delete_Cluster Except:" + str(e)
        return False
