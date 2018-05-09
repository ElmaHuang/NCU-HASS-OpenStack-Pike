import sys
import time

import Preprocess

sys.path.insert(0, '..')
from HASS.InstanceFailures import InstanceFailure
from HASS.NovaClient import NovaClient

instance_thread = InstanceFailure()
CMD = "ifconfig eth0 down"
wrong_ip = "7.7.7.7"


def run():
    instance_id = Preprocess.create_instance()
    try:
        ip = Preprocess._get_instance_ip()
        print "check vm boot"
        time.sleep(30)
        #ssh = Preprocess.create_ssh_client(ip)
        #stdin, stdout, stderr = Preprocess._remote_exec(ssh, CMD)
        result = instance_thread.pingInstance(ip)
        if result:
            print "detect network isolation successfully"
            result = instance_thread.pingInstance(wrong_ip)
            if not result:
                return True
            else:
                return False
        else:
            print "detect network isolation fail"
        return False
    except Exception as e:
        print "UT_Detect_Network Except:" + str(e)
        return False
    finally:
        Preprocess._deleteInstance()


def reboot_vm(instance_id, detect_time=5):
    novaClient = NovaClient.getInstance()
    novaClient.hardReboot(instance_id)
    result = False
    try:
        boot = _check_boot_up(detect_time)
        return boot
    except Exception as e:
        print "UT_Detect_Network reboot_vm-Except:" + str(e)
        return False


def _check_boot_up(time_out=30):
    try:
        while time_out > 0:
            state = Preprocess._get_instance_status()
            if "ACTIVE" in state:
                return True
            else:
                time_out -= 1
                time.sleep(1)
        return False
    except Exception as e:
        print "UT_Detect_Network check-boot-Except:" + str(e)
        return False
