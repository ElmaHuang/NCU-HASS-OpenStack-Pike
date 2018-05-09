import sys

sys.path.insert(0, '..')
from HASS.HAInstance import HAInstance

CLUSTER_ID = "cluster01"
NODE_NAME = ["compute2"]
instance = ['4ae736be-0247-4a19-be24-5f46ca7e2920', u'instance-unit-test', u'compute', u'ACTIVE',
            {u'provider': [u'192.168.0.224']}]


def run():
    HAInstance.init()
    try:
        HAInstance.addInstance(CLUSTER_ID, instance)
        instance_list = HAInstance.getInstanceList()
        if len(instance_list) == 1:
            return True
        else:
            return False
    except Exception as e:
        print "UT_Add_HA_Instance Except:" + str(e)
        return False
