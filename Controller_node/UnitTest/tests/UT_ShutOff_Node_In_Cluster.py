import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager
from HASS.IPMINodeOperator import Operator

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2"]
HOST = "compute2"


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ipmi_operator = Operator()

    try:
        result = ipmi_operator.shutOffNode(HOST)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_ShutOff_Node_In_Cluster Except:" + str(e)
        return False
    finally:
        ClusterManager.deleteNode(cluster_id, NODE_NAME[0], write_DB=False)
