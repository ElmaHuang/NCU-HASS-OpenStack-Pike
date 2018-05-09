import sys

sys.path.insert(0, '..')
from HASS.InstanceFailures import InstanceFailure

instance_thread = InstanceFailure()
fail_index = [5, 2]


def run():
    try:
        crash_event = instance_thread.transformDetailToString(fail_index[0], fail_index[1])
        recover = instance_thread._findfailure(crash_event, "")
        if recover == "Crash":
            print "detect vm crash successfully"
            return True
        else:
            print "detect vm crash fail"
        return False
    except Exception as e:
        print "UT_Detect_VM_Crash Except:" + str(e)
        return False
