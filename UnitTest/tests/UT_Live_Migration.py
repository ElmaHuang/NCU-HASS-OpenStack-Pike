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
TARGET_HOST = "compute2"


def run():
    instance_id = Preprocess.create_with_provider_instance()
    novaClient = NovaClient.getInstance()

    try:
        novaClient.liveMigrateVM(instance_id, TARGET_HOST)
        if novaClient.getInstanceHost(instance_id) == "compute2":
            return True
        else:
            return False
    except Exception as e:
        print str(e)
        return False
    finally:
        pass
        # Postprocess.deleteInstance()
