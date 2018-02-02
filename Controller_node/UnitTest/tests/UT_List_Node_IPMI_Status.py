import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1", "compute2"]


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)

    try:
        result = ClusterManager.listNode(cluster_id)
        node_list = result.data.get("node_list")
        print node_list
        check = False
        for node in node_list:
            node_name = node[0]
            ipmi_status = node[2]
            if node_name == "compute2":
                if ipmi_status:
                    check = True
            if node_name == "compute1":
                if not ipmi_status:
                    check = True
        return check
    except Exception as e:
        print "UT_LIst_Node_IPMI_Status Except:" + str(e)
        return False
    finally:
        for node_name in NODE_NAME:
            ClusterManager.deleteNode(cluster_id, node_name, write_DB=False)
