import sys
import time

sys.path.insert(0, '..')
from HASS.Instance import Instance
from HASS.NovaClient import NovaClient
import Config, Postprocess, Preprocess

CLUSTER_ID = "clusterid"
HOST = "compute2"
TARGET_HOST = "compute1"
STATUS = "ACTIVE"
NETWORK = "network"


def run():
    instance_id = Preprocess.create_with_provider_instance()
    instance = Instance(instance_id, Config.INSTANCE_NAME, HOST, STATUS, NETWORK)
    time.sleep(10)
    # fail_node = Node(HOST, CLUSTER_ID)
    # target_host = Node(TARGET_HOST, CLUSTER_ID)
    novaClient = NovaClient.getInstance()

    try:
        host = novaClient.liveMigrateVM(instance_id, TARGET_HOST)
        if host == TARGET_HOST:
            return True
        else:
            return False
    except Exception as e:
        print "UT_Live_Migration Except:" + str(e)
        return False
    finally:
        Postprocess.deleteInstance()
