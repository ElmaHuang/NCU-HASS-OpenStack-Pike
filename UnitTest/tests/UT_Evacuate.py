import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager
from Instance import Instance
from Node import Node
from NovaClient import NovaClient
import Preprocess
import Postprocess
import Config

CLUSTER_ID = "clusterid"
HOST = "compute1"
TARGET_HOST = "compute2"
STATUS = "ACTIVE"
NETWORK = "network"


def run():
    instance_id = Preprocess.create_with_provider_instance()
    instance = Instance(instance_id, Config.INSTANCE_NAME, HOST, STATUS, NETWORK)

    fail_node = Node(HOST, CLUSTER_ID)
    target_host = Node(TARGET_HOST, CLUSTER_ID)
    novaClient = NovaClient.getInstance()

    try:
        novaClient.evacuate(instance, target_host, fail_node)
        if novaClient.getInstanceHost(instance_id) == TARGET_HOST:
            return True
        else:
            return False
    except Exception as e:
        print str(e)
        return False
    finally:
        Postprocess.deleteInstance()
