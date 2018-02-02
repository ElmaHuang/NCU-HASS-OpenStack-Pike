import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute1"


def run():
    ipmi_operator = Operator()
    try:
        result = ipmi_operator.rebootNode(HOST)
        if result.code == "succeed":
            return False
        return True
    except Exception as e:
        print "UT_Reboot_Wrong_Node Except:" + str(e)
        return False
