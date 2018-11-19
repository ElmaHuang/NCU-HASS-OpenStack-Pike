#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains instance data structure.
##########################################################


from __future__ import print_function

from NovaClient import NovaClient


class Instance(object):
    def __init__(self, id, name, host, status, network):
        self.nova_client = NovaClient.getInstance()
        self.id = id
        self.name = name
        self.host = host
        self.network = network
        self.ext_net = self.getExternalNetwork(self.network)
        self.status = status

    def updateInfo(self):
        self.status = self.nova_client.getInstanceState(self.id)
        self.host = self.nova_client.getInstanceHost(self.id)
        self.network = self.nova_client.getInstanceNetwork(self.id)
        self.ext_net = self.getExternalNetwork(self.network)

    def getInfo(self):
        info = []
        try:
            self.updateInfo()
            info = [self.id, self.name, self.host, self.status, self.network]
        except Exception as e:
            print("instance--getInfo-fail" + str(e))
        finally:
            return info

    def getExternalNetwork(self, network):
        """

        :param network: 
        :return: 
        """
        ext_ip = None
        for router_name, ip_list in network.iteritems():
            for ip in ip_list:
                ext_ip = self.nova_client.getInstanceExternalNetwork(ip)
        return ext_ip

    '''
    def sendUpdate(self):
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.connect((self.host ,5001))
        #ip = so.recv(1024)
        so.send(str(self.network))
        #print ip
        so.close()

    def sendDeleteIP(self):
        so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.connect((self.host, 5001))
        # ip = so.recv(1024)
        so.send()
        # print ip
        so.close()
    
    def isPowerOn(self):
        return self.nova_client.isInstancePowerOn(self.id)

    def hasVolume(self):
        return self.nova_client.isInstanceGetVolume(self.id)
    '''
