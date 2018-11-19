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


from __future__ import print_function

import logging
import subprocess
import time

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
        self.nova_client = NovaClient.get_instance()
        self.server = RPCServer.get_rpc_server()
        self.vm_name = None
        self.failed_info = None
        self.recovery_type = ""

    def recover_instance(self, fail_vm):
        """

        :param fail_vm: 
        :return: 
        """
        # fail_vm = ['instance-00000344', 'Failed',State]
        self.vm_name = fail_vm[0]
        self.failed_info = fail_vm[1]
        self.recovery_type = fail_vm[2]
        result = False
        print("start recover:" + self.recovery_type)
        # print Failure.SHUTOFF_OR_DELETED.value
        if self.recovery_type in Failure.OS_CRASH.value or self.recovery_type in Failure.OS_HANGED.value:
            result = self.hard_reboot_instance(self.vm_name)
        elif self.recovery_type in Failure.MIGRATED.value:
            result = self.update_db(self.vm_name)
        elif self.recovery_type in Failure.SHUTOFF_OR_DELETED.value:
            result = self.delete_instance(self.vm_name)
        elif self.recovery_type in Failure.NETWORK_ISOLATION.value:
            if self.soft_reboot_instance(self.vm_name):
                print("soft reboot successfully")
                result = self.check_network_state(self.failed_info)
                if result:
                    message = "ping vm successfully"
                    print(message)
                    logging.info(message)
                else:
                    message = "ping vm fail"
                    print(message)
                    logging.error(message)
        print("recover %s finish" % self.recovery_type)
        print("result :", result)
        HAInstance.update_ha_instance()
        return result

    def hard_reboot_instance(self, fail_instance_name):
        """

        :param fail_instance_name: 
        :return: 
        """
        instance = self.get_ha_instance(fail_instance_name)
        self.nova_client.hard_reboot(instance.id)
        return self.check_recover_state(instance.id)

    def soft_reboot_instance(self, fail_instance_name):
        """

        :param fail_instance_name: 
        :return: 
        """
        instance = self.get_ha_instance(fail_instance_name)
        self.nova_client.soft_reboot(instance.id)
        return self.check_recover_state(instance.id)

    def update_db(self, fail_instance_name):
        # instance = self.get_ha_instance(fail_instance_name)
        try:
            instance = self.get_ha_instance(fail_instance_name)
            if self.check_recover_state(instance.id):
                self.server.updateAllCluster()
                return True
            else:
                raise Exception("live migration time out")
        except Exception as e:
            logging.error("RecoveryInstance update_db--except:" + str(e))
            return False

    def delete_instance(self, fail_instance_name):
        """

        :param fail_instance_name: 
        :return: 
        """
        instance = self.get_ha_instance(fail_instance_name)
        # state = self.check_destroy_state(instance.id)
        # if not state:
        #     return "instance state is ACTIVE!!!"
        try:
            result = self.server.deleteInstance(instance.cluster_id, instance.id, False)
            if result["code"] == "succeed":
                return True
            return False
        except Exception as e:
            logging.error("RecoveryInstance delete_instance--except:" + str(e))
            return False

    def check_network_state(self, ip, time_out = 60):
        """

        :param ip: 
        :param time_out: 
        :return: 
        """
        # check network state is up
        while time_out > 0:
            try:
                print("ping ", ip)
                response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip],
                                                   stderr = subprocess.STDOUT,
                                                   universal_newlines = True)
                logging.info("recover network isolation success")
                return True
            except subprocess.CalledProcessError:
                time.sleep(1)
                time_out -= 1
        logging.error("recover vm network isolation fail")
        return False

    def get_ha_instance(self, name):
        """

        :param name: 
        :return: 
        """
        return HAInstance.get_instance(name)

    def check_recover_state(self, id, check_timeout = 60):
        """

        :param id: 
        :param check_timeout: 
        :return: 
        """
        while check_timeout > 0:
            state = self.nova_client.get_instance_state(id)
            if "ACTIVE" in state:
                return True
            else:
                time.sleep(1)
                check_timeout -= 1
        return False


if __name__ == '__main__':
    a = RecoveryInstance()
    # a.soft_reboot_instance("instance-000000cc")
    # a.nova_client.soft_reboot("ef554e3d-72a2-46fb-91e1-274f6de85f23")
