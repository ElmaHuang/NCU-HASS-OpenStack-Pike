import subprocess
import threading
import time
import libvirt
# import ConfigParse
import InstanceEvent
from HAInstance import HAInstance
from RecoveryInstance import RecoveryInstance


class InstanceFailure(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.host = host
        self.recovery_vm = RecoveryInstance()
        self.failed_instances = []
        # failed_instance
        '''
        while True:
            self._startDetection()
            time.sleep(2)
        '''

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def run(self):
        while True:
            try:
                self.createLibvirtDetectionThread()
                # libvirt_connection
                libvirt_connection = self.getLibvirtConnection()
                libvirt_connection.domainEventRegister(self._checkVMState, None)  # event handler(callback,self)
                libvirt_connection.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,
                                                          self._checkVMWatchdog, None)
                # Adds a callback to receive notifications of arbitrary domain events occurring on a domain.

                # self._checkNetwork()
            except Exception as e:
                print "failed to run detection method , please check libvirt is alive.exception :", str(e)
            finally:
                while True:
                    time.sleep(5)
                    if self.failed_instances != []:
                        # libvirt_connect.close()
                        try:
                            result = self.recoverFailedInstance()
                            if not result:
                                print "recovery " + str(
                                    self.failed_instances) + "fail or the instance is not HA instance."
                            else:
                                print "recovery " + str(self.failed_instances) + " success"
                        except Exception as e:
                            print str(e)
                        finally:
                            self.failed_instances = []
                    elif not libvirt_connection.isAlive() == 1:
                        # 1 if alive, 0 if dead, -1 on error
                        break
                        # time.sleep(5)

    def createLibvirtDetectionThread(self):
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()
        except Exception as e:
            print "failed to create libvirt detection thread " + str(e)

    def getLibvirtConnection(self):
        try:
            connection = libvirt.openReadOnly('qemu:///system')
            if connection == None:
                print "failed to open connection to qemu:///system"
            else:
                return connection
        except Exception as e:
            print "failed to open connection --exception" + str(e)

    def _checkVMState(self, connect, domain, event, detail, opaque):
        # event:cloume,detail:row
        print "domain name :", domain.name(), " domain id :", domain.ID(), "event:", event, "detail:", detail
        recovery_type = "State"
        event_string = self.transformDetailToString(event, detail)
        failedString = InstanceEvent.Event_failed
        print "state event string :", event_string
        if event_string in failedString:
            self.failed_instances.append([domain.name(), event_string, recovery_type])
            # print "fail instance--State:",self.failed_instances

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
            self.failed_instances.append([domain.name(), action, recovery_type])
            # print "fail instance--WD:",self.failed_instances

    def transformDetailToString(self, event, detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]

    def recoverFailedInstance(self):
        print "get ha vm"
        ha_instance = HAInstance.getInstanceList()
        print "ha list :", ha_instance
        # check instance is protected
        self.checkRecoveryVM(ha_instance)
        # any instance shoule be recovery
        if self.failed_instances != []:
            for fail_instance in self.failed_instances:
                try:
                    result = self.recovery_vm.recoverInstance(fail_instance)
                    return result
                except Exception as e:
                    print str(e)
        else:  # fail instance is not HA instance
            return True

    def checkRecoveryVM(self, ha_instance):
        # find all fail_vm in self.failed_instances is ha vm or not
        if ha_instance == {}:
            return
        for failed_vm in self.failed_instances[:]:
            for id, instance in ha_instance.iteritems():
                if failed_vm[0] not in instance.name:
                    self.failed_instances.remove(failed_vm)

    '''
    def readlog(self):
        ha_instance = []
        with open('./HAInstance.py', 'r') as ff:
            for lines in ff:
                instances = lines.split("\n")
                #[['id:8f3340f3-0c48-4333-98e3-96f62df41f21', 'name:instance-00000346', 'host:compute3', 'status:ACTIVE', "network:{'selfservice':", "['192.168.1.8',", "'192.168.0.212']}\n"]]
                for instance in instances:
                    #id:219046ce-1c1e-4a73-ac53-4cacafd08e79 name:instance-00000342 host:compute3 status:ACTIVE network:{'provider': ['192.168.0.207']}
                    instance = self._splitString(instance)
                    if instance != []:ha_instance.append(instance)
        ff.close()
        return ha_instance

    def _splitString(self,string):
        instance = []
        inst = re.sub('[\[\]{}\'"]', '', string)
        #['id:8f3340f3-0c48-4333-98e3-96f62df41f21', ' name:instance-00000346', ' host:compute3', ' status:ACTIVE', ' network:selfservice:', ' 192.168.1.8', '', ' 192.168.0.212']
        inst = "".join(inst)
        inst = inst.split(" ")
        for str in inst:
            str = re.split(r'[:\s]\s*', str)
            for c in str :
                if c =="":
                    str.remove(c)
            if str != []:instance.append(str)
            #[
            # ['id', '8f3340f3-0c48-4333-98e3-96f62df41f21'],
            # ['name', 'instance-00000346'],
            # ['host', 'compute3'],
            # ['status', 'ACTIVE'],
            # ['network', 'selfservice'],
            # ['192.168.1.8'],
            # ['192.168.0.212']
            # ]
        return instance
    '''


if __name__ == '__main__':
    a = InstanceFailure()
    a.start()
    # a._splitString("[['id:8f3340f3-0c48-4333-98e3-96f62df41f21', 'name:instance-00000346', 'host:compute3', 'status:ACTIVE', \"network:{'selfservice':\", \"['192.168.1.8',\", \"'192.168.0.212']}")
