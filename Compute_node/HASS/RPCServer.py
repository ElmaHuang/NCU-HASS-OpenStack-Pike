#########################################################
#:Date: 2018/2/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   Using SimpleXMLRPC client
##########################################################


import ConfigParser
import xmlrpclib


class RPCServer():
    config = ConfigParser.RawConfigParser()
    config.read('hass_node.conf')
    authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                               "rpc_password") + "@" + config.get("rpc",
                                                                                                                  "rpc_controller") + ":" + config.get(
        "rpc", "rpc_bind_port")
    # self.authUrl = "http://user:0928759204@192.168.0.112:61209"
    server = xmlrpclib.ServerProxy(authUrl)

    @staticmethod
    def getRPCServer():
        return RPCServer.server
