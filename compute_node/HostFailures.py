import libvirt
import time
import sys
import threading
import subprocess

class HostFailure(threading.Thread):
    def __init__(self,version):
        threading.Thread.__init__(self)
        self.libvirt_uri = "qemu:///system"
        self.version = version
        self.str = ""

    def run(self):
        while True:
            self.clearlog()
            result = self.check_services(self.version)
            print "sevice fail:",result
            self.writelog(result)
            time.sleep(5)

    def check_services(self, version):
        self.version = version
        message = ""
        #check libvirt
        if not self._checkLibvirt():
            message = "libvirt;"
            #self.str = message+"\n"
        #check nova-compute
        if not self._checkNovaCompute():
            message += "nova;"
            #self.str +=  message+"\n"
        if not self._checkQEMUKVM():
            message += "qemukvm;"
            #self.str += message+"\n"
        return message

    def _checkLibvirt(self):
        try:
            conn = libvirt.open(self.libvirt_uri)
            if not conn:
                return False
        except Exception as e:
            print "libvirt exception:",str(e)
            return False
        return True

    def _checkNovaCompute(self):
        try:
            output = subprocess.check_output(['ps', '-A'])
            if "nova-compute" not in output:
                return False
        except Exception as e:
            print "nova-compute exception:",str(e)
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
            print "qemu exception:",str(e)
            return False
        return True

    def clearlog(self):
        with open('./host_fail.log', 'w'): pass
        #with open('./log/sucess.log', 'w'): pass

    def writelog(self,str):
        with open('./host_fail.log', 'a') as f:
            f.write(str)
            f.close()
'''
if __name__ == '__main__':
    a = HostFailure(16)
    a.start()
    try:
        while True:
            pass
    except:
        sys.exit(1)
'''