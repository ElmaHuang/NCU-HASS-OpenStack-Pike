import sys

sys.path.insert(0, '..')
from HASS.Instance import Instance
from HASS.Node import Node
from HASS.NovaClient import NovaClient
import Config, Postprocess, Preprocess

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
        print "UT_Evacuate Except:" + str(e)
        return False
    finally:
        Postprocess.deleteInstance()
