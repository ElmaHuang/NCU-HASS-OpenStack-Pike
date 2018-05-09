import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute3"


def run():
    operator = Operator()
    try:
        result = operator.getAllInfoByNode(HOST)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_Get_All_Sensor_Value_Wrong_Node Except:" + str(e)
        return True
