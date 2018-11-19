import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute2"


def run():
    ipmi_operator = Operator()
    try:
        result = ipmi_operator.rebootNode(HOST)
        if result.code == "succeed":
            return True
        return False
    except Exception as e:
        print "UT_Reboot_Node Except:" + str(e)
        return False
