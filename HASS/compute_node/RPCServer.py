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
