import sys

sys.path.insert(0, '..')
from HASS.InstanceFailures import InstanceFailure

instance_thread = InstanceFailure()
fail_index = [5, 3]


def run():
    """

    :return: 
    """
    try:
        crash_event = instance_thread.transform_detail_to_string(fail_index[0], fail_index[1])
        recover = instance_thread._find_failure(crash_event, "")
        if recover == "Migration":
            print "detect vm migration successfully"
            return True
        else:
            print "detect vm migration fail"
        return False
    except Exception as e:
        print "UT_Detect_Live_Migration Except:" + str(e)
        return False

# def reboot_vm(instance_id, detect_time=5):
#     novaClient = NovaClient.get_instance()
#     novaClient.hard_reboot(instance_id)
#     result = False
#     try:
#         boot = _check_boot_up(detect_time)
#         return boot
#     except Exception as e:
#         print "UT_Detect_Network reboot_vm-Except:" + str(e)
#         return False
#
#
# def _check_boot_up(time_out=30):
#     try:
#         while time_out > 0:
#             state = Preprocess._get_instance_status()
#             if "ACTIVE" in state:
#                 return True
#             else:
#                 time_out -= 1
#                 time.sleep(1)
#         return False
#     except Exception as e:
#         print "UT_Detect_Network check-boot-Except:" + str(e)
#         return False
