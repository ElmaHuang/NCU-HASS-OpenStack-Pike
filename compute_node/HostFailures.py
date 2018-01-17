import asyncore
import socket
import ConfigParser
import subprocess
import libvirt


class HostFailures(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        config = ConfigParser.RawConfigParser()
        config.read('hass_node.conf')
        self.host = None
        self.port = int(config.get("polling", "listen_port"))
        self.version = int(config.get("version", "version"))
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind(('', self.port))
        self.libvirt_uri = "qemu:///system"
        print "host failure port:", self.port

    def handle_read(self):
        data, addr = self.recvfrom(2048)
        # print 'request from: ', addr
        print data
        if "polling request" in data:
            check_result = self.check_services()
            if check_result == "":
                self.sendto("OK", addr)
            else:
                check_result = "error:" + check_result
                self.sendto(check_result, addr)

    def check_services(self):
        message = ""
        # check libvirt
        if not self._checkLibvirt():
            message = "libvirt;"
        # check nova-compute
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
        except Exception as e:
            print str(e)
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
