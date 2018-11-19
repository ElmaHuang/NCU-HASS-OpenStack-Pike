import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

NODE_NAME = ["compute2"]


def run():
    ClusterManager.init()
    cluster_id = "wrong id"

    try:
        result = ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_Add_Node_Wrong_Cluster_ID Except:" + str(e)
        return False
