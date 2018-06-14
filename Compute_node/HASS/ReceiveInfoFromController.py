#########################################################
#:Date: 2018/2/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   Receive update message from controller node by socket
##########################################################


from __future__ import print_function

import socket
import threading

from HAInstance import HAInstance


class ReceiveInfoFromController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', 5001))
        self.s.listen(5)
        '''
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass_node.conf')
        self.authUrl = "http://" + self.config.get("rpc", "rpc_username") + ":" + self.config.get("rpc",
                                                                                                  "rpc_password") + 
                                                                                                  "@" + self.config.get(
            "rpc", "rpc_controller") + ":" + self.config.get("rpc", "rpc_bind_port")
        # self.authUrl = "http://user:0928759204@192.168.0.112:61209"
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        '''

    def run(self):
        while True:
            cs, addr = self.s.accept()
            print("addr:", addr)
            data = cs.recv(1024)
            print(data)
            if "update instance" in data:
                print("get update mesg from controller")
                HAInstance.update_ha_instance()
        # for instance in instance_list[:]:
        #     # [self.id, self.name, self.host, self.status, self.network]
        #     vm = Instance(ha_instance=instance)
        #     HAInstance.add_instance(vm)
