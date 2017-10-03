import socket
import asyncore
import socket
import sys
import ConfigParser
import libvirt
import subprocess

class DetectionAgent():
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('hass_node.conf')
        self.port = int(config.get("polling","listen_port"))
        
    def startListen(self):
        print "create listen thread"
        server = PollingHandler('192.168.1.21', self.port)
        asyncore.loop()
    

class PollingHandler(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.libvirt_uri = "qemu:///system"
        print port
        
    def handle_read(self):
        data, addr = self.recvfrom(2048)
        # print 'request from: ', addr
        check_result = self.check_services()
        print data
        if data == "polling request":
            if check_result == "":
                self.sendto("OK", addr)
            else:
                check_result = "error:" + check_result
                self.sendto(check_result, addr)
    
    def check_services(self):
        message = ""
        #check libvirt
        if not self._checkLibvirt():
            message = "libvirt;"
        #check nova-compute
        if not self._checkNovaCompute():
            message += "nova;"
        if not self._checkQEMUKVM():
            message += "qemu-kvm"
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
            if "start/running" not in output:
                return False
        except:
            return False
        return True
    
if __name__ == "__main__":
    server = PollingHandler('192.168.1.21', 20000)
    asyncore.loop()

