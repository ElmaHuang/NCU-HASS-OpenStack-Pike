import logging
import subprocess
import sys
import threading

import libvirt

# import ConfigParse
import InstanceEvent
from HAInstance import HAInstance
from RecoveryInstance import RecoveryInstance


class InstanceFailure(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.recovery_vm = RecoveryInstance()
        self.libvirt_uri = "qemu:///system"

        # self.failed_instances = []

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def run(self):
        while True:
            try:
                self.createLibvirtDetectionThread()
                libvirt_connection = self.getLibvirtConnection()
                libvirt_connection.domainEventRegister(self._checkVMState, None)  # event handler(callback,self)
                libvirt_connection.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,
                                                          self._checkVMWatchdog, None)
                # Adds a callback to receive notifications of arbitrary domain events occurring on a domain.

                # self._checkNetwork()
                while True:
                    if not self.checkLibvrtConnect(libvirt_connection):
                        # 1 if alive, 0 if dead, -1 on error
                        break

            except Exception as e:
                message = "failed to run detection method , please check libvirt is alive.exception :" + str(e)
                logging.error(message)
                sys.exit(1)
            # finally:
            #     while True:
            #         if not self.checkLibvrtConnect(libvirt_connection):
            #             # 1 if alive, 0 if dead, -1 on error
            #             break
            #         time.sleep(5)
            #         if self.failed_instances != []:
            #             # libvirt_connect.close()
            #             try:
            #                 result = self.recoverFailedInstance(fail_instance=)
            #                 if not result:
            #                     print "recovery " + str(
            #                         self.failed_instances) + "fail or the instance is not HA instance."
            #                 else:
            #                     print "recovery " + str(self.failed_instances) + " success"
            #             except Exception as e:
            #                 print str(e)
            #             finally:
            #                 self.failed_instances = []
            #         elif not libvirt_connection.isAlive() == 1:
            #             libvirt_connection.close()
            #             # 1 if alive, 0 if dead, -1 on error
            #             break
            #             # time.sleep(5)

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
        recovery_type = self._findfailure(event_string)
        if recovery_type != "":
            fail_instance = [domain.name(), event_string, recovery_type]
            logging.info(str(fail_instance))
            result = self.recoverFailedInstance(fail_instance=fail_instance)
            print self.showResult(result)

    def _findfailure(self, event_string):
        recovery_type = ""
        if self._check_vm_crash(event_string):
            recovery_type = "Crash"
        elif self._check_vm_destroyed(event_string):
            recovery_type = "Delete"
        elif self._check_vm_migrated(event_string):
            recovery_type = "Migration"
        return recovery_type

    def _check_vm_crash(self, event_string):
        failed_string = InstanceEvent.Event_failed
        if event_string == failed_string:
            print "crash--state event string :", event_string
            return True
        return False

    def _check_vm_destroyed(self, event_string):
        destroyed_string = InstanceEvent.Event_destroyed
        print destroyed_string
        if event_string in destroyed_string:
            print "vm be shut off"
            print "destroy--state event string :", event_string
            return True
        return False

    def _check_vm_migrated(self, event_string):
        migrated_string = InstanceEvent.Event_migrated
        if "Migrated" in event_string and event_string in migrated_string:
            print "migrate--state event string :", event_string
            return True
        return False

    def _checkNetwork(self):
        recovery_type = "Network"
        ha_instance = HAInstance.getInstanceList()
        for id, instance in ha_instance.iteritems():
            ip = instance.network_provider
            try:
                response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', ip], stderr=subprocess.STDOUT,
                                                   universal_newlines=True)
            except subprocess.CalledProcessError:
                self.failed_instances.append([instance.name, ip, recovery_type])

    def _checkVMWatchdog(self, connect, domain, action, opaque):
        print "domain name:", domain.name(), " domain id:", domain.ID(), "action:", action
        recovery_type = "Watchdog"
        watchdog_string = InstanceEvent.Event_watchdog_action
        # print "watchdog event string:",watchdogString
        if action in watchdog_string:
            fail_instance = [domain.name(), action, recovery_type]
            result = self.recoverFailedInstance(fail_instance=fail_instance)
            print self.showResult(result)
            # self.failed_instances.append([domain.name(), action, recovery_type])

    def transformDetailToString(self, event, detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def recoverFailedInstance(self, fail_instance):
        print "get ha vm"
        result = False
        ha_instance_list = HAInstance.getInstanceList()
        # check instance is protected
        check = self.checkRecoveryVM(fail_instance, ha_instance_list)
        if check:
            try:
                result = self.recovery_vm.recoverInstance(fail_instance)
            except Exception as e:
                logging.error("InstanceFailures recoverFailedInstance Except:" + str(e))
                print str(e)
            finally:
                return result
        elif not check:
            # not ha vm
            return check

    def checkRecoveryVM(self, failed_instance, ha_instance_list):
        # find all fail_vm in self.failed_instances is ha vm or not
        result = None
        if not ha_instance_list:
            return result
        for ha_instance in ha_instance_list:
            if failed_instance[0] in ha_instance.name:
                result = True
        return result

    def showResult(self, result):
        if result is None:
            return '\033[92m' + "[it is not HA instance] " + '\033[0m'
        elif result:
            return '\033[92m' + "[recover instance success] " + '\033[0m'
        else:
            return '\033[91m' + "[recover instance fail] " + '\033[0m'


if __name__ == '__main__':
    a = InstanceFailure()
    a.start()
    # a._splitString("[['id:8f3340f3-0c48-4333-98e3-96f62df41f21', 'name:instance-00000346', 'host:compute3', 'status:ACTIVE', \"network:{'selfservice':\", \"['192.168.1.8',\", \"'192.168.0.212']}")
