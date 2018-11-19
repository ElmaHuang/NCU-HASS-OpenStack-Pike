import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute2"
TYPE = ["Wrong"]


def run():
    operator = Operator()
    try:
        result = operator.getNodeInfoByType(HOST, TYPE)
        if result.code == "succeed":
            return False
        else:
            return True
    except Exception as e:
        print "UT_Get_Sensor_Value_By_Type Except:" + str(e)
        return False
