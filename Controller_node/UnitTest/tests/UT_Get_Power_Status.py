import sys

sys.path.insert(0, '..')
from HASS.IPMIModule import IPMIManager

HOST = "compute2"


def run():
    ipmi_manager = IPMIManager()
    try:
        result = ipmi_manager.getPowerStatus(HOST)
        if result == "OK":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Get_Power_Status Except:" + str(e)
        return False
