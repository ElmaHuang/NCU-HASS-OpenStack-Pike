import sys
import time

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator
from HASS.IPMIModule import IPMIManager

HOST = "compute2"


def run():
    ipmi_operator = Operator()
    ipmi_manager = IPMIManager()
    result = ipmi_manager.shutOffNode(HOST)
    time.sleep(20)
    if result.code != "succeed":
        print "shutoff node fail"
    try:
        result = ipmi_operator.startNode(HOST)
        if result.code == "succeed":
            return True
        return False
    except Exception as e:
        print "UT_Start_Node Except:" + str(e)
        return False
