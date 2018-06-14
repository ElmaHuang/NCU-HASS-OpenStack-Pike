import sys

sys.path.insert(0, '..')
from HASS.InstanceFailures import InstanceFailure

instance_thread = InstanceFailure()
fail_index = [5, 1]
not_exist_vm = ""


def run():
    """

    :return: 
    """
    try:
        crash_event = instance_thread.transform_detail_to_string(fail_index[0], fail_index[1])
        recover = instance_thread._find_failure(crash_event, not_exist_vm)
        if recover == "Delete":
            print "detect delete vm successfully"
            return True
        else:
            print "detect delete vm fail"
        return False
    except Exception as e:
        print "UT_Detect_Delete_Instance Except:" + str(e)
        return False
