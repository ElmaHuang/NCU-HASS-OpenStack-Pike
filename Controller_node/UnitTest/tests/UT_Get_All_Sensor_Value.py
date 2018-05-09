import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute2"


def run():
    operator = Operator()
    try:
        result = operator.getAllInfoByNode(HOST)
        if result.code == "succeed":
            return True
        else:
            return False
    except Exception as e:
        print "UT_Get_All_Sensor_Value Except:" + str(e)
        return False
