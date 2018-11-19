import sys
import time

import Preprocess

sys.path.insert(0, '..')
from HASS.NovaClient import NovaClient


def run():
    """

    :return: 
    """
    try:
        novaClient = NovaClient.get_instance()
        instance_id = Preprocess.create_instance()
        novaClient.soft_reboot(instance_id)
        time.sleep(10)
        return True
    except Exception as e:
        print "UT_Soft_Reboot Except:" + str(e)
        return False
    finally:
        # time.sleep(10)
        Preprocess._deleteInstance()
