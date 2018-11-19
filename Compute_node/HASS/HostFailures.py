#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class which detects whether computing nodes happens error or not.
##########################################################


from __future__ import print_function

import ConfigParser
import logging
import socket
import subprocess
import threading

import libvirt


class HostFailures(threading.Thread):
    def __init__(self):
        # asyncore.dispatcher.__init__(self)
        threading.Thread.__init__(self)
        config = ConfigParser.RawConfigParser()
        config.read('hass_node.conf')
        self.host = None
        self.port = int(config.get("polling", "listen_port"))
        self.version = int(config.get("version", "version"))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', self.port))
        # self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.set_reuse_addr()
        # self.bind(('', self.port))
        self.libvirt_uri = "qemu:///system"
        print("host failure port:", self.port)

    def run(self):
        while True:
            data, addr = self.s.recvfrom(1024)
            print(data)
            if "polling request" in data:
                check_result = self.check_services()
                if check_result == "":
                    self.s.sendto("OK", addr)
                else:
                    check_result = "error:" + check_result
                    self.s.sendto(check_result, addr)

    '''
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
    '''

    def check_services(self):
        message = ""
        # check libvirt
        if not self._check_libvirt():
            message = "libvirt;"
        # check nova-compute
        if not self._check_nova_compute():
            message += "nova;"
        if not self._check_qemu_kvm():
            message += "qemukvm;"
        return message

    def _check_libvirt(self):
        try:
            conn = libvirt.open(self.libvirt_uri)
            if not conn:
                return False
        except Exception as e:
            logging.error(str(e))
            return False
        conn.close()
        return True

    def _check_nova_compute(self):
        try:
            output = subprocess.check_output(['ps', '-A'])
            if "nova-compute" not in output:
                return False
        except Exception as e:
            logging.error(str(e))
            return False
        return True

    def _check_qemu_kvm(self):
        try:
            output = subprocess.check_output(['service', 'qemu-kvm', 'status'])
            if self.version == 14:
                if "start/running" not in output:
                    return False
            elif self.version == 16:
                if "active" not in output:
                    return False
        except Exception as e:
            logging.error(str(e))
            return False
        return True
