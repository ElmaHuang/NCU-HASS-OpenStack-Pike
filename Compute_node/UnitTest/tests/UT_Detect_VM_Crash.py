import sys

sys.path.insert(0, '..')
from HASS.InstanceFailures import InstanceFailure

instance_thread = InstanceFailure()
fail_index = [5, 2]


def run():
    """

    :return: 
    """
    try:
        crash_event = instance_thread.transform_detail_to_string(fail_index[0], fail_index[1])
        recover = instance_thread._find_failure(crash_event, "")
        if recover == "Crash":
            print "detect vm crash successfully"
            return True
        else:
            print "detect vm crash fail"
        return False
    except Exception as e:
        print "UT_Detect_VM_Crash Except:" + str(e)
        return False
