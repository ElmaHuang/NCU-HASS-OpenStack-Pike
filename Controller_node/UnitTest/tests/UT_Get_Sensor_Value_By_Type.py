import sys

sys.path.insert(0, '..')
from HASS.IPMINodeOperator import Operator

HOST = "compute2"
TYPE = ["Inlet Temp"]


def run():
    operator = Operator()
    try:
        result = operator.getNodeInfoByType(HOST, TYPE)
        if result.code == "succeed":
            print result.data.get("Info")
            return True
        else:
            return False
    except Exception as e:
        print "UT_Get_Sensor_Value_By_Type Except:" + str(e)
        return False
