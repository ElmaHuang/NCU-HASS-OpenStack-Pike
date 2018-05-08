##########################################################
#:Date: 2018/2/12
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class which detects whether virtual machine happens error or not.
###########################################################


import logging
import subprocess
import sys
import threading
import time

import libvirt

# import ConfigParse
import InstanceEvent
from HAInstance import HAInstance
from NovaClient import NovaClient
from RecoveryInstance import RecoveryInstance


class InstanceFailure(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.nova_client = NovaClient.getInstance()
        self.recovery_vm = RecoveryInstance()
        self.libvirt_uri = "qemu:///system"
        HAInstance.updateHAInstance()

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def run(self):
        while True:
            try:
                self.createLibvirtDetectionThread()
                libvirt_connection = self.getLibvirtConnection()
                # time.sleep(5)
                libvirt_connection.domainEventRegister(self._checkVMState, None)  # event handler(callback,self)
                libvirt_connection.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,
                                                          self._checkVMWatchdog, None)
                # Adds a callback to receive notifications of arbitrary domain events occurring on a domain.
                while True:
                    #self._checkNetwork()
                    time.sleep(5)
                    if not self.checkLibvrtConnect(libvirt_connection):
                        # 1 if alive, 0 if dead, -1 on error
                        break

            except Exception as e:
                message = "failed to run detection method , please check libvirt is alive.exception :" + str(e)
                logging.error(message)
                sys.exit(1)

    def createLibvirtDetectionThread(self):
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()
        except Exception as e:
            message = "failed to create libvirt detection thread " + str(e)
            print message
            logging.error(message)

    def checkLibvrtConnect(self, connection):
        try:
            if connection.isAlive() == 1:
                return True
            else:
                return False
        except Exception as e:
            mes = "fail to check libvirt connection isAlive()" + str(e)
            connection.close()
            logging.error(mes)
            return False

    def getLibvirtConnection(self):
        try:
            connection = libvirt.openReadOnly(self.libvirt_uri)
            if connection is None:
                print "failed to open connection to qemu:///system"
            else:
                return connection
        except Exception as e:
            message = "failed to open connection --exception" + str(e)
            print message
            logging.error(message)

    def _checkVMState(self, connect, domain, event, detail, opaque):
        # event:cloume,detail:row
        print "domain name :", domain.name(), " domain id :", domain.ID(), "event:", event, "detail:", detail
        event_string = self.transformDetailToString(event, detail)
        print "state event string :", event_string
        recovery_type = self._findfailure(event_string, domain)
        if recovery_type != "":
            fail_instance = [domain.name(), event_string, recovery_type]
            logging.info(str(fail_instance))
            result = self.recoverFailedInstance(fail_instance=fail_instance)
            print self.showResult(result)

    def _findfailure(self, event_string, domain):
        recovery_type = ""
        if self._check_vm_crash(event_string):
            recovery_type = "Crash"
            return recovery_type
        elif self._check_vm_destroyed(event_string, domain.name()):
            recovery_type = "Delete"
            return recovery_type
        elif self._check_vm_migrated(event_string):
            recovery_type = "Migration"
            #time.sleep(5)
        return recovery_type

    def _check_vm_crash(self, event_string):
        failed_string = InstanceEvent.Event_failed
        if event_string in failed_string:
            print "crash--state event string :", event_string
            return True
        return False

    def _check_vm_destroyed(self, event_string, instance_name):
        destroyed_string = InstanceEvent.Event_destroyed
        if event_string in destroyed_string:
            print "destroy--state event string :", event_string
            return self.checkDestroyState(instance_name)

    def _check_vm_migrated(self, event_string):
        migrated_string = InstanceEvent.Event_migrated
        if "Migrated" in event_string and event_string in migrated_string:
            print "migrate--state event string :", event_string
            time.sleep(5)
            return True
        return False

    def _checkNetwork(self):
        recovery_type = "Network"
        ha_instance_list = HAInstance.getInstanceList()
        if not ha_instance_list:
            return
        for ha_instance in ha_instance_list:
            if not ha_instance.network_provider:
                return
            ip = ha_instance.network_provider[0]
            print "check net %s" % ip
            if not self.pingInstance(ip):
                if self.checkNetworkDown(ha_instance):
                    fail_instance = [ha_instance.name, ip, recovery_type]
                    # print fail_instance
                    result = self.recoverFailedInstance(fail_instance=fail_instance)
                    print self.showResult(result)

    def _checkVMWatchdog(self, connect, domain, action, opaque):
        print "domain name:", domain.name(), " domain id:", domain.ID(), "action:", action
        recovery_type = "Watchdog"
        watchdog_string = InstanceEvent.Event_watchdog_action
        if action in watchdog_string:
            fail_instance = [domain.name(), action, recovery_type]
            result = self.recoverFailedInstance(fail_instance=fail_instance)
            print self.showResult(result)

    def transformDetailToString(self, event, detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def recoverFailedInstance(self, fail_instance):
        # print "get ha vm"
        result = False
        print "start recover fail instance"
        print "update HA Instance"
        HAInstance.updateHAInstance()  # for live migration host info
        ha_instance_list = HAInstance.getInstanceList()
        # check instance is protected
        check = self.checkRecoveryVM(fail_instance, ha_instance_list)  # True/None
        if check:
            try:
                result = self.recovery_vm.recoverInstance(fail_instance)
            except Exception as e:
                logging.error("InstanceFailures recoverFailedInstance Except:" + str(e))
                print str(e)
            finally:
                return result  # True/False
        elif not check:
            return check  # None

    def checkRecoveryVM(self, failed_instance, ha_instance_list):
        # find all fail_vm in self.failed_instances is ha vm or not
        # print ha_instance_list
        result = None
        if not ha_instance_list:
            return result
        for ha_instance in ha_instance_list:
            if failed_instance[0] in ha_instance.name:
                result = True
        return result

    def checkDestroyState(self, instance_name, check_timeout=10):
        instance = HAInstance.getInstance(instance_name)
        print "start check %s is destroyed or shutoff" % instance_name
        # result = True
        while check_timeout > 0:
            time.sleep(5)
            state = self.getInstanceState(instance.id)
            if "ACTIVE" not in state:
                if state is None:
                    # Deleted
                    check_timeout -= 1
                else:
                    # ShutOff
                    return False
            else:
                # Reboot
                return False
        return True

    def checkNetworkDown(self, instance, time_out=5):
        # check network state is down
        print "start to check network state second time"
        while time_out > 0:
            time.sleep(5)
            state = self.getInstanceState(instance.id)
            # maybe vm just be reboot
            if "ACTIVE" in state:
                network_state = self.pingInstance(instance.ip)
                if network_state:
                    # network state is not down
                    return False
                    # network state is temporary down
                time_out -= 1
            else:
                # vm is deleted or shutoff
                return False
        return True

    def pingInstance(self, ip):
        try:
            response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                               universal_newlines=True)
            print "ping %s success" % ip
            return True
        except Exception as e:
            print "ping %s fail" % ip
            print "pingInstance--Exception:", str(e)
            return False

    def getInstanceState(self, instance_id):
        try:
            state = self.nova_client.getInstanceState(instance_id)
            return state
        except Exception as e:
            print "getInstanceState--Exception:", str(e)
            return None

    def showResult(self, result):
        if result is None:
            return '\033[92m' + "[it is not HA instance] " + '\033[0m'
        elif result:
            return '\033[92m' + "[recover instance success] " + '\033[0m'
        elif not result:
            return '\033[91m' + "[recover instance fail] " + '\033[0m'
        else:
            return result


if __name__ == '__main__':
    a = InstanceFailure()
    a.start()
