import logging
import subprocess

from enum import Enum

from HAInstance import HAInstance
from NovaClient import NovaClient
from RPCServer import RPCServer


class Failure(Enum):
    OS_CRASH = "Crash"
    OS_HANGED = "Watchdog"
    MIGRATED = "Migration"
    SHUTOFF_OR_DELETED = "Delete"
    NETWORK_ISOLATION = "Network"


class RecoveryInstance(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.server = RPCServer.getRPCServer()
        self.vm_name = None
        self.failed_info = None
        self.recovery_type = ""

    def recoverInstance(self, fail_vm):

        # fail_vm = ['instance-00000344', 'Failed',State]
        self.vm_name = fail_vm[0]
        self.failed_info = fail_vm[1]
        self.recovery_type = fail_vm[2]
        result = False
        print "start recover:" + self.recovery_type
        print Failure.SHUTOFF_OR_DELETED.value
        if self.recovery_type in Failure.OS_CRASH.value or self.recovery_type in Failure.OS_HANGED.value:
            result = self.hardRebootInstance(self.vm_name)
        elif self.recovery_type in Failure.MIGRATED.value:
            result = self.updateDB()
        elif self.recovery_type in Failure.SHUTOFF_OR_DELETED.value:
            result = self.deleteInstance(self.vm_name)
        elif self.recovery_type in Failure.NETWORK_ISOLATION.value:
            result = self.softRebootInstance(self.vm_name)
            if result:
                print "soft reboot successfully"
                result = self.pingInstance(self.vm_name)
                if result:
                    message = "ping vm successfully"
                    print message
                    logging.info(message)
                else:
                    message = "ping vm fail"
                    print message
                    logging.error(message)
        if result:
            self._updateHAInstance()
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
        except Exception as e:
            logging.error("RecoveryInstance updateDB--except:" + str(e))
            return False

    def deleteInstance(self, fail_instance_name):
        try:
            instance = self.getHAInstance(fail_instance_name)
            result = self.server.deleteInstance(instance.cluster_id, instance.id, False)
            if result["code"] == "succeed":
                return True
            return False
        except Exception as e:
            print str(e)
            logging.error("RecoveryInstance deleteInstance--except:" + str(e))

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

    def _updateHAInstance(self):
        HAInstance.init()
        HAInstance.getInstanceFromController()
        print "update HA Instance"
