import sys

sys.path.insert(0, '..')
from HASS.NovaClient import NovaClient
import Preprocess, Postprocess

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
        print "UT_LIve_Migration Except:" + str(e)
        return False
    finally:
        Postprocess.deleteInstance()
