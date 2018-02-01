import subprocess

from HAInstance import HAInstance
from NovaClient import NovaClient
from RPCServer import RPCServer


class RecoveryInstance(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.server = RPCServer.getRPCServer()
        self.vm_name = None
        self.failed_info = None
        self.recovery_type = None

    def recoverInstance(self, fail_vm):
        # fail_vm = ['instance-00000344', 'Failed',State]
        self.vm_name = fail_vm[0]
        self.failed_info = fail_vm[1]
        self.recovery_type = fail_vm[2]
        result = False
        if "Crash" or "Watchdog" in self.recovery_type:
            result = self.hardRebootInstance(self.vm_name)

        elif "Migration" in self.recovery_type:
            result = self.updateDB()

        elif "Delete" in self.recovery_type:
            result = self.deleteInstance(self.vm_name)

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

    def updateDB(self):
        # instance = self.getHAInstance(fail_instance_name)
        try:
            self.server.updateAllCluster()
            return True
        except:
            return False

    def deleteInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        result = self.server.deleteInstance(instance.cluster_id, instance.id, False)
        if result["code"] == "succeed":
            return True
        return False

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
