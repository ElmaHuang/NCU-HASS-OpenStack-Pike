import subprocess
from NovaClient import NovaClient
from HAInstance import HAInstance


class RecoveryInstance(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.vm_name = None
        self.failed_info = None
        self.recovery_type = None

    def recoverInstance(self, fail_vm):
        # fail_vm = ['instance-00000344', 'Failed',State]
        self.vm_name = fail_vm[0]
        self.failed_info = fail_vm[1]
        self.recovery_type = fail_vm[2]
        if "State" or "Watchdog" in self.recovery_type:
            result = self.hardRebootInstance(self.vm_name)
            return result
            # self.softReboot()
        elif "Network" in self.recovery_type:
            result = self.softRebootInstance(self.vm_name)
            if result:
                print "soft reboot successfully"
                result = self.pingInstance(self.vm_name)
                if result:
                    print "ping vm successfully"
                else:
                    print "ping vm fail"
            return result

    def hardRebootInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.hardReboot(instance.id)
        result = self.checkState(instance.id)
        return result

    def softRebootInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.softReboot(instance.id)
        result = self.checkState(instance.id)
        return result

    def pingInstance(self, name):
        instance = self.getHAInstance(name)
        ip = instance.network_provider
        try:
            response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                               universal_newlines=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def getHAInstance(self, name):
        ha_vm = HAInstance.getInstance(name)
        return ha_vm

    def checkState(self, id, check_timeout=60):
        while check_timeout > 0:
            state = self.nova_client.getInstanceState(id)
            if "ACTIVE" in state:
                return True
            else:
                check_timeout -= 1
        return False
