import libvirt
import threading
import time

import libvirt

# import ConfigParser
from compute_node import InstanceEvent


class InstanceFailure():
    def __init__(self):
        #self.config = ConfigParser.RawConfigParser()
        #self.config.read('hass_node.conf')
        self.clearlog()
        while True:
            self._startDetection()
            time.sleep(2)
    '''
    def run(self):
        #all instance
        while(True):
            self.clearlog()
            #for instance in all_nstance:
            result = self.check_instance(instance)
            self.writelog(result)
    '''

    def __virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def _startDetection(self):
        #eventLoopThread = None
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()
            # open the connection to self qemu
            connect = libvirt.openReadOnly('qemu:///system')
            if connect == None:
                return "failed to open connection to qemu:///system"
        except:
            return "failed to open connection to qemu:///system"
        try:
            connect.domainEventRegister(self._checkVMState,None)
            connect.domainEventRegisterAny(None,libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,self._checkVMWatchdog,None)
            while True:
                if not connect.isAlive():
                    return
                time.sleep(2)
        except Exception as e:
            print "failed to run startDetection method in VMDetector, please check libvirt is alive.exception :",str(e)
        finally:
            connect.close()

    def _checkVMState(self, connect, domain, event, detail, opaque):
        #event:cloume,detail:row
        print "domain name :",domain.name()," domain id :",domain.ID(),"event:",event,"detail:",detail
        failedString = InstanceEvent.Event_failed
        event_string = self.transformDetailToString(event,detail)
        if event_string in failedString:
            self.writelog(domain.name())
        #return True

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain:",domain.name()," ",domain.ID(),"action:",action
        #watchdogString = self.config.get("vm_watchdog_event","Event_watchdog_action")
        #if action in watchdogString:
            #self.writelog(domain.name())

    def _checkNetwork(self):
        pass
        #if vm network isolation:
            #self.writelog(domain.name())


    def transformDetailToString(self,event,detail):
        stateString = InstanceEvent.Event_string
        return stateString[event][detail]


    def clearlog(self):
        with open('./instance_fail.log', 'w'): pass
        #with open('./log/sucess.log', 'w'): pass

    def writelog(self,str):
        with open('./instance_fail.log', 'a') as f:
            f.write(str)
            f.close()
if __name__ == '__main__':
    a = InstanceFailure()
    #a._startDetection()