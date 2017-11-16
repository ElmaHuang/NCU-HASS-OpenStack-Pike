import libvirt
import subprocess

class HostFailure():
    def __init__(self):
        self.libvirt_uri = "qemu:///system"

    def check_services(self, version):
        self.version = version
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