import sys

sys.path.insert(0, '..')
from HASS.ClusterManager import ClusterManager
from HASS.Instance import Instance
from HASS.Node import Node
from HASS.NovaClient import NovaClient
from HASS.RecoveryManager import RecoveryManager
import Config, Postprocess, Preprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1", "compute2"]
HOST = "compute2"
TARGET_HOST = "compute1"
STATUS = "ACTIVE"
NETWORK = "network"


def run():
    ClusterManager.init()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)

    instance_id = Preprocess.create_with_provider_instance()
    instance = Instance(instance_id, Config.INSTANCE_NAME, HOST, STATUS, NETWORK)

    fail_node = Node(HOST, CLUSTER_ID)
    target_host = Node(TARGET_HOST, CLUSTER_ID)
    #novaClient = NovaClient.getInstance()

    try:
        RecoveryManager.recoverVM(instance, target_host, fail_node)
        if novaClient.getInstanceHost(instance_id) == TARGET_HOST:
            return True
        else:
            return False
    except Exception as e:
        print "UT_Evacuate Except:" + str(e)
        return False
    finally:
        Postprocess.deleteInstance()
