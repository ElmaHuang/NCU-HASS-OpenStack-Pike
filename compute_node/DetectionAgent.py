import socket
import asyncore
import socket
import sys
import ConfigParser
import xmlrpclib
import time
#import libvirt
#import subprocess
from HostFailures import  HostFailure
from InstanceFailures import InstanceFailure
from RecoveryInstance import RecoveryInstance

class DetectionAgent():
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('hass_node.conf')
        self.port = int(config.get("polling","listen_port"))
        self.version = int(config.get("version","version"))
        
    def startListen(self):
        print "create listen thread"
        server = PollingHandler('', self.port, self.version)
        asyncore.loop()
    

class PollingHandler(asyncore.dispatcher):
    def __init__(self, host, port, version):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((host, port))
        #self.libvirt_uri = "qemu:///system"
        self.version = version
        self.host = host
        self.recover = RecoveryInstance()
        self.host_detection = HostFailure(self.version)
        self.host_detection.start()
        self.instance_detection = InstanceFailure(self.host)
        self.instance_detection.start()
        self.authUrl = "http://user:0928759204@192.168.0.112:61209"
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        #self.server.test_auth_response()
        print port
        
    def handle_read(self):
        data, addr = self.recvfrom(2048)
        # print 'request from: ', addr
        print data
        if "polling request" in data:
            check_result = self.check_host()
            if check_result == "":
                self.sendto("OK", addr)
            else:
                check_result = "error:" + check_result
                self.sendto(check_result, addr)

        #instancelist = self.getHAInstance()
        '''
        if instancelist != []:
            #instance_detection = InstanceFailure(instancelist)
            time.sleep(5)
            check_result = self.check_instance()
            for fail_instance in check_result:
                for instance in instancelist:
                    if instance[1] not in instance:
                        #self.sendto("OK", addr)
                        continue
                    else:
                        recovery_result = self.recover.rebootInstance(fail_instance)
                        #self.sendto(check_result, addr)
                        if recovery_result == False:
                            recovery_result = self.recover.rebuildInstance(fail_instance)
                            if recovery_result == False:
                             self.server.deleteInstacne(fail_instance)
        '''
    '''
    def check_services(self):
        message = ""
        #check libvirt
        if not self._checkLibvirt():
            message = "libvirt;"
        #check nova-compute
        if not self._checkNovaCompute():
            message += "nova;"
        if not self._checkQEMUKVM():
            message += "qemukvm;"
        return message

    def _checkLibvirt(self):
        try:
            conn = libvirt.open(self.libvirt_uri)
            if not conn:
                return False
        except:
            return False
        return True
    def _checkNovaCompute(self):
        try:
            output = subprocess.check_output(['ps', '-A'])
            if "nova-compute" not in output:
                return False
        except:
            return False
        return True
    def _checkQEMUKVM(self):
        try:
            output = subprocess.check_output(['service', 'qemu-kvm', 'status'])
            if self.version == 14:
                if "start/running" not in output:
                    return False
            elif self.version == 16:
                if "active" not in output:
                    return False
        except Exception as e:
            print str(e)
            return False
        return True
    '''
    def check_host(self):
        result = ""
        with open('./host_fail.log', 'r') as fs:
            for line in fs:
                result += line
        fs.close()
        return result

    def check_instance(self):
        result = []
        with open('./instance_fail.log', 'r') as f:
            for line in f:
                #line: instance-00000333:watchdog fail
                result.append(line)
        f.close()
        return result

    def getHAInstance(self):
        host_instance = []
        cluster_list = self.server.listCluster()
        for cluster in cluster_list:
            clusterId = cluster[0]
            instance_list = self.server.listInstance(clusterId)["instanceList"]
            for instance in instance_list:
                if instance[2] == self.host:
                    host_instance.append(instance)
        return host_instance

def main():
    agent = DetectionAgent()
    agent.startListen()
    try:
        while True:
            pass
    except:
        sys.exit(1)

if __name__ == "__main__":
    main()

