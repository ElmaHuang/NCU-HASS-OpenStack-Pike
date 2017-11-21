import subprocess
import threading


class InstanceFailure(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.fail_instance = []
        #all_instance = virsh instance list

    def run(self):
        #all instance
        while(True):
            self.clearlog()
            #for instance in all_nstance:
            result = self.check_instance(instance)
            self.writelog(result)

    def check_instance(self,instance):
        #print instance
        #[['0e0ce568-4ae3-4ade-b072-74edeb3ae58c', 'instance-00000310', 'compute3', 'ACTIVE']]
        result = ""
        if not self._checkOS():
            result = "os"
        if not self._checkNetwork():
            result += "network"
        return [instance,result]

    def _checkOS(self):
        #output = subprocess.check_output([virsh instance os])
        #if os hanged :
            #return False
        return True

    def _checkNetwork(self):
        #if vm network isolation:
            #return False
        return True

    def clearlog(self):
        with open('./instance_fail.log', 'w'): pass
        #with open('./log/sucess.log', 'w'): pass

    def writelog(self,str):
        with open('./instance_fail.log', 'a') as f:
            f.write(str)
            f.close()