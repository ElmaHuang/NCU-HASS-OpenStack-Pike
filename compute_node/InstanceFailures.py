import subprocess
class InstanceFailure():

    def check_instance(self,instance):
        #print instance
        #[['0e0ce568-4ae3-4ade-b072-74edeb3ae58c', 'instance-00000310', 'compute3', 'ACTIVE']]
        result = ""
        if not self._checkOS():
            result = "os"
        if not self._checkNetwork():
            result += "network"
        return result

    def _checkOS(self):
        #output = subprocess.check_output([virsh instance os])
        #if os hanged :
            #return False
        return True

    def _checkNetwork(self):
        #if vm network isolation:
            #return False
        return True