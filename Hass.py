#!/usr/bin/python
"""
HASS Service
Using SimpleXMLRPC library handle http requests
Client can use function in Hass class directly
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from base64 import b64decode
import ConfigParser
import logging
import os
import sys

from RecoveryManager import RecoveryManager
from ClusterManager import ClusterManager
from Operator import Operator
#from IPMIModule import IPMIManager

class Hass (object):

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')

        log_level = logging.getLevelName(self.config.get("log", "level"))
        logFilename = self.config.get("log", "location")
        dir = os.path.dirname(logFilename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        logging.basicConfig(filename=logFilename, level=log_level, format="%(asctime)s [%(levelname)s] : %(message)s")
        #ipmi_manager = IPMIManager()
        self.ClusterManager = ClusterManager()

        self.Operator = Operator()
        self.Recovery = RecoveryManager()

    def test_auth_response(self):
    #Unit tester call this function to get successful message if authenticate success.
        return "auth success"
        
    def createCluster(self, name, nodeList=[]):
        result = ClusterManager.createCluster(name)
        if result["code"] == "0":
            if nodeList != []:
                addNode_result = ClusterManager.addNode(result["clusterId"], nodeList)
            else :
                addNode_result = {"code":0, "clusterId":result["clusterId"], "message":"not add any node."}
                    
            if addNode_result["code"] == "0":
                return "0;Create HA cluster and add computing node success, cluster uuid is %s , %s" % (result["clusterId"] , addNode_result["message"])
            else:
                return "0;The cluster is created.(uuid = "+result["clusterId"]+") But,"+ addNode_result["message"]
        else:
            return result["code"]+";"+result["message"]

    def deleteCluster(self, uuid, test=False):
        result = self.ClusterManager.deleteCluster(uuid)
        return result["code"]+";"+result["message"]
    
    def listCluster(self):
        result = self.ClusterManager.listCluster()
        return result
    
    def addNode(self, clusterId, nodeList, test=False):
        result = self.ClusterManager.addNode(clusterId, nodeList)
        return result["code"]+";"+result["message"]

    def deleteNode(self, clusterId, nodename, test=False):
        result = self.ClusterManager.deleteNode(clusterId, nodename)
        return result["code"]+";"+result["message"]
        
    def listNode(self, clusterId) :
        result = self.ClusterManager.listNode(clusterId)
        if result["code"]== "0":
            return result["code"]+";"+result["nodeList"]
        else:
            return result["code"]+";"+result["message"]
            
    def startNode(self, nodeName):
        result = self.Operator.Start_Node(nodeName)
        return result["code"] + ";" + result["message"]

    def shutOffNode(self, nodeName):
        result = self.Operator.Shut_Off_Node(nodeName)
        return result["code"] + ";" + result["message"]

    def rebootNode(self, nodeName):
        result = self.Operator.Reboot_Node(nodeName)
        return result["code"] + ";" + result["message"]

    def getAllInfoOfNode(self, nodeName):
        result = self.Operator.getAllInfoOfNode(nodeName)
        if result["code"] == "0":
            return result["code"]+";"+result["info"]
        else:
            return result["code"] + ";" + result["message"]

    def getNodeInfoByType(self, nodeName, sensorType):
        result = self.Operator.getNodeInfoByType(nodeName, sensorType)
        if result["code"] == "0":
            return result["code"], result["info"]
        else: 
            return result["code"] + ";" + result["message"]

    def addInstance(self, clusterId, instanceId):
        result = self.ClusterManager.addInstance(clusterId, instanceId)
        return result["code"]+";"+result["message"]
    
    def deleteInstance(self, clusterId, instanceId):
        result = self.ClusterManager.deleteInstance(clusterId, instanceId)
        return result["code"]+";"+result["message"]
    
    def listInstance(self, clusterId) :
        result = self.ClusterManager.listInstance(clusterId)
        if result["code"]== "0":
            return result["code"]+";"+result["instanceList"]
        else:
            return result["code"]+";"+result["message"]
            
    def recoveryVM(self, clusterId, nodeName):
        result = self.Recovery.recoveryVM(clusterId, nodeName)

    def removeNodeFromCluster(self, clusterId, nodeName):
        result = recovery.remove_node_from_cluster(clusterId, nodeName)

    def recoveryByShutOffNode(self, clusterId, nodeName, option):
        result = recovery.recovery_by_shut_Off_Node(clusterId, nodeName)
        return result

    def recoveryServiceFailure(self, clusterId, nodeName, service_list):
        result = recovery.recovery_service_failure(clusterId, nodeName, service_list)
        return result

    def recoveryIPMIDaemonFailure(self, clusterId, nodeName, option):
        result = recovery.recovery_ipmi_daemon_failure(nodeName)
        return result

    def recoveryWatchdogDaemonFailure(self, clusterId, nodeName, option):
        result = recovery.recovery_watchdog_daemon_failure(nodeName)
        return result

    def recoveryOSHanged(self, clusterId, nodeName, option):
        result = recovery.recovery_os_hanged(clusterId, nodeName)
        return result

    def recoveryNetworkFailure(self, clusterId, nodeName, option):
        result = recovery.recovery_network_failure(clusterId, nodeName)
        return result

    def recoveryPowerOff(self, clusterId, nodeName, option):
        result = recovery.recovery_power_off(clusterId, nodeName)
        return result

class RequestHandler(SimpleXMLRPCRequestHandler):
    #   Handle RPC request from remote user, and suport access authenticate.
    #
    #   HTTP basic access authentication are encoded with Base64 in transit, but not
    #   encrypted or hashed in any way. Authentication field contain authentication
    #   method, username and password combined into a string. If request not contain
    #   authentication header or contain not correct username and password, it will
    #   return 401 error code. Otherwise, handle request and return response.

    def __init__(self, request, client_address, server):
        # initialize rpc server and get client ip address. call parent initial method.
        rpc_paths = ('/RPC2',)
        self.clientip = client_address[0]
        SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)

    def authenticate(self, headers):
        # split authentication header, decode with Base64 and check username and password
        auth = headers.get('Authorization')
        try:
            (basic, encoded) = headers.get('Authorization').split(' ')
        except:
            logging.info("Hass RequestHandler - No authentication header, request from %s", self.clientip)
            return False
        else:
            (basic, encoded) = headers.get('Authorization').split(' ')
            assert basic == 'Basic', 'Only basic authentication supported'
            encodedByteString = encoded.encode()
            decodedBytes = b64decode(encodedByteString)
            decodedString = decodedBytes.decode()
            (username, password) = decodedString.split(':')
            config = ConfigParser.RawConfigParser()
            config.read('hass.conf')
            if username == config.get("rpc", "rpc_username") and password == config.get("rpc", "rpc_password"):
                print "Login"
                return True
            else:
                logging.info("Hass RequestHandler - Authentication failed, request from %s", self.clientip)
                return False

    def parse_request(self):
        # parser request, get authentication header and send to authenticate().
        if SimpleXMLRPCRequestHandler.parse_request(self):
            if self.authenticate(self.headers):
                # logging.info("Hass RequestHandler - Authentication success, request from %s", self.clientip)
                return True
            else:
                self.send_error(401, 'Authentication failed')
                return False
        else:
            logging.info("Hass RequestHandler - Authentication failed, request from %s", self.clientip)
            return False


def main():
    hass = Hass()
    server = SimpleXMLRPCServer(('',int(hass.config.get("rpc", "rpc_bind_port"))), requestHandler=RequestHandler, allow_none = True, logRequests=False)
    server.register_introspection_functions()
    server.register_multicall_functions()
    server.register_instance(hass, allow_dotted_names=True)

    print "HASS Server ready"
    try:
        server.serve_forever()
    except:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
