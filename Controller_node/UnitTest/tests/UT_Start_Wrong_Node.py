import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute"


def run():
    ipmi_operator = Operator()
    try:
        result = ipmi_operator.startNode(HOST)
        if result.code == "succeed":
            return False
        return True
    except Exception as e:
        print "UT_Start_Wrong_Node Except:" + str(e)
        return False
