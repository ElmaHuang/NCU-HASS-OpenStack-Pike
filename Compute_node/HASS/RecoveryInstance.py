#########################################################
#:Date: 2018/2/12
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains recovery methods.
##########################################################


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
        # print Failure.SHUTOFF_OR_DELETED.value
        if self.recovery_type in Failure.OS_CRASH.value or self.recovery_type in Failure.OS_HANGED.value:
            result = self.hardRebootInstance(self.vm_name)
        elif self.recovery_type in Failure.MIGRATED.value:
            result = self.updateDB()
        elif self.recovery_type in Failure.SHUTOFF_OR_DELETED.value:
            result = self.deleteInstance(self.vm_name)
        elif self.recovery_type in Failure.NETWORK_ISOLATION.value:
            if self.softRebootInstance(self.vm_name):
                print "soft reboot successfully"
                result = self.chekNetworkState(self.failed_info)
                if result:
                    message = "ping vm successfully"
                    print message
                    logging.info(message)
                else:
                    message = "ping vm fail"
                    print message
                    logging.error(message)
        print "recover %s finish" % self.recovery_type
        # print result
        HAInstance.updateHAInstance()
        return result

    def hardRebootInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.hardReboot(instance.id)
        return self.checkRecoverState(instance.id)

    def softRebootInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        self.nova_client.softReboot(instance.id)
        return self.checkRecoverState(instance.id)

    def updateDB(self):
        # instance = self.getHAInstance(fail_instance_name)
        try:
            self.server.updateAllCluster()
            return True
        except Exception as e:
            logging.error("RecoveryInstance updateDB--except:" + str(e))
            return False

    def deleteInstance(self, fail_instance_name):
        instance = self.getHAInstance(fail_instance_name)
        # state = self.checkDestroyState(instance.id)
        # if not state:
        #     return "instance state is ACTIVE!!!"
        try:
            result = self.server.deleteInstance(instance.cluster_id, instance.id, False)
            if result["code"] == "succeed":
                return True
            return False
        except Exception as e:
            print str(e)
            logging.error("RecoveryInstance deleteInstance--except:" + str(e))

    def chekNetworkState(self, ip, time_out=60):
        # check network state is up
        while time_out > 0:
            try:
                response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                                   universal_newlines=True)
                logging.info("recover network isolation success")
                return True
            except subprocess.CalledProcessError:
                time_out -= 1
        logging.error("recover vm network isolation fail")
        return False

    def getHAInstance(self, name):
        return HAInstance.getInstance(name)

    def checkRecoverState(self, id, check_timeout=60):
        while check_timeout > 0:
            state = self.nova_client.getInstanceState(id)
            if "ACTIVE" in state:
                return True
            else:
                check_timeout -= 1
        return False


if __name__ == '__main__':
    a = RecoveryInstance()
    # a.softRebootInstance("instance-000000cc")
    # a.nova_client.softReboot("ef554e3d-72a2-46fb-91e1-274f6de85f23")
    print a.pingInstance("192.168.0.232")
