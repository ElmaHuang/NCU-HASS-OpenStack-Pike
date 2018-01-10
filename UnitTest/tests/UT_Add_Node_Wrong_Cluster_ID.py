import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

NODE_NAME = ["compute1"]


def run():
    ClusterManager.init()
    cluster_id = "wrong id"

    try:
        result = ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
        if result["code"] == "0":
            return False
        else:
            return True
    except:
        return True
