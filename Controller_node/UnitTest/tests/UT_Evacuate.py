import sys
import time

sys.path.insert(0, '..')
from HASS.Instance import Instance
from HASS.Node import Node
from HASS.NovaClient import NovaClient
import Postprocess, Preprocess

CLUSTER_ID = "clusterid"
HOST = "compute2"
TARGET_HOST = "compute1"
STATUS = "ACTIVE"
NETWORK = {}


def run():
    novaClient = NovaClient.getInstance()
    instance_id = Preprocess.create_with_provider_instance()
    instance = Instance(instance_id, novaClient.getInstanceName(instance_id), HOST, STATUS, NETWORK)
    time.sleep(20)
    fail_node = Node(HOST, CLUSTER_ID)
    target_host = Node(TARGET_HOST, CLUSTER_ID)
    try:
        novaClient.evacuate(instance, target_host, fail_node)
        time.sleep(20)
        if novaClient.getInstanceHost(instance_id) == TARGET_HOST:
            return True
        else:
            return False
    except Exception as e:
        print "UT_Evacuate Except:" + str(e)
        return False
    finally:
        fail_node.undefineInstance(instance)
        Postprocess.deleteInstance()
