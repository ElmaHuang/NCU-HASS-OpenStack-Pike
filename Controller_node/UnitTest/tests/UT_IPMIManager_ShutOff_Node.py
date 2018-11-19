import sys
import time

sys.path.insert(0, '..')
from HASS.IPMIModule import IPMIManager

HOST = "compute2"


def run(check_timeout=60):
    ipmi_manager = IPMIManager()
    try:
        result = ipmi_manager.shutOffNode(HOST)

        while check_timeout > 0:
            power_status = ipmi_manager.getPowerStatus(HOST)
            if power_status == "Error" and result.code == "succeed":
                time.sleep(60)
                return True
            check_timeout -= 1
            time.sleep(1)
        return False
    except Exception as e:
        print "UT_ShutOff_Node Except:" + str(e)
        return False
