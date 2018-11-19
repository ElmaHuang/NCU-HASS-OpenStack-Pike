import sys
import time

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator
from HASS.IPMIModule import IPMIManager

HOST = "compute2"


def run():
    ipmi_operator = Operator()
    ipmi_manager = IPMIManager()

    try:
        result = ipmi_operator.shutOffNode(HOST)
        time.sleep(20)
        if result.code == "succeed":
            print "boot node"
            result = ipmi_manager.startNode(HOST)
            if result.code == "succeed":
                print "boot node successfully"
            else:
                print "boot node fail"
            return True
        return False
    except Exception as e:
        print "UT_ShutOff_Node Except:" + str(e)
        return False
