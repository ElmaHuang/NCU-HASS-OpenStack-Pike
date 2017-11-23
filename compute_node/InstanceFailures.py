import libvirt
import socket
import threading
import time
# import ConfigParser
import InstanceEvent
from recvIP import recvIPThread

class InstanceFailure(threading.Thread):
    def __init__(self,host):
        threading.Thread.__init__(self)
        self.host = host
        self.clearlog()
        self.recv = recvIPThread()
        self.recv.start()
        '''
        while True:
            self._startDetection()
            time.sleep(2)
        '''
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

    def run(self):
        self.createDetectionThread()
        connect = libvirt.openReadOnly('qemu:///system')
        if connect == None:
            print "failed to open connection to qemu:///system"
        #while True:
        try:
            connect.domainEventRegister(self._checkVMState,None)
            connect.domainEventRegisterAny(None,libvirt.VIR_DOMAIN_EVENT_ID_WATCHDOG,self._checkVMWatchdog,None)
        except Exception as e:
            print "failed to run startDetection method in VMDetector, please check libvirt is alive.exception :",str(e)
        finally:
            #self.close()
            #connect.close()
            time.sleep(5)

    def createDetectionThread(self):
        try:
            # set event loop thread
            libvirt.virEventRegisterDefaultImpl()
            eventLoopThread = threading.Thread(target=self.__virEventLoopNativeRun, name="libvirtEventLoop")
            eventLoopThread.setDaemon(True)
            eventLoopThread.start()
            # open the connection to self qemu
        except Exception as e:
            return str(e)

    def _checkVMState(self, connect, domain, event, detail, opaque):
        #event:cloume,detail:row
        print "domain name :",domain.name()," domain id :",domain.ID(),"event:",event,"detail:",detail
        event_string = self.transformDetailToString(event,detail)
        failedString = InstanceEvent.Event_failed
        if event_string in failedString:
            self.writelog(domain.name())
        #return True

    def _checkNetwork(self):
        pass
        #for instance in self.instance_list:
            #print instance
        #if vm network isolation:
            #self.writelog(domain.name())

    def _checkVMWatchdog(self, connect,domain, action, opaque):
        print "domain:",domain.name()," ",domain.ID(),"action:",action
        #watchdogString = self.config.get("vm_watchdog_event","Event_watchdog_action")
        #if action in watchdogString:
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
    a.start()