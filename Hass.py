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

from ClusterManager import ClusterManager
from IPMIModule import IPMIManager

# Declare the configure file here. if you want to change configure file name, please modify : hass.conf.
config = ConfigParser.RawConfigParser()
config.read('hass.conf')

# Set log file here. if you want to change log format, please modify : %(asctime)s [%(levelname)s] : %(message)s.
log_level = logging.getLevelName(config.get("log", "level"))
logFilename=config.get("log", "location")
dir = os.path.dirname(logFilename)
if not os.path.exists(dir):
    os.makedirs(dir)
logging.basicConfig(filename=logFilename,level=log_level, format="%(asctime)s [%(levelname)s] : %(message)s")

# recovery = None
# if len(sys.argv) == 2:
#     print "System Test = ", sys.argv[1]
#     recovery = Recovery(system_test = sys.argv[1])
# else:
# # Declare Recovery class. You need to ensure that there is only one object. So I declare it as global variable.
#     recovery = Recovery()

ipmi_manager = IPMIManager()
ClusterManager = ClusterManager()

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
                #logging.info("Hass RequestHandler - Authentication success, request from %s", self.clientip)
                return True
            else:
                self.send_error(401, 'Authentication failed')
                return False
        else:
            logging.info("Hass RequestHandler - Authentication failed, request from %s", self.clientip)
            return False
        

class Hass (object):
#   The SimpleRPCServer class
#   Declare method here, and client can call it directly.
#   All of methods just process return data from recovery module

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
        result = recovery.deleteCluster(uuid)
        return result["code"]+";"+result["message"]
    
    def listCluster(self):
        result = recovery.listCluster()
        return result
    
    def addNode(self, clusterId, nodeList, test=False):
        result = ClusterManager.addNode(clusterId, nodeList)               
        return result["code"]+";"+result["message"]

    def deleteNode(self, clusterId, nodename, test=False):
        result = recovery.deleteNode(clusterId, nodename)
        return result["code"]+";"+result["message"]
        
    def listNode(self, clusterId) :
        result = recovery.listNode(clusterId)
        if result["code"]== "0":
            return result["code"]+";"+result["nodeList"]
        else:
            return result["code"]+";"+result["message"]
            
    def startNode(self, nodeName):
        result = ipmi_manager.startNode(nodeName)
        return result["code"] + ";" + result["message"]

    def shutOffNode(self, nodeName):
        result = ipmi_manager.shutOffNode(nodeName)
        return result["code"] + ";" + result["message"]

    def rebootNode(self, nodeName):
        result = ipmi_manager.rebootNode(nodeName)
        return result["code"] + ";" + result["message"]

    def getAllInfoOfNode(self, nodeName):
        result = ipmi_manager.getAllInfoOfNode(nodeName)
        if result["code"] == "0":
            return result["code"]+";"+result["info"]
        else:
            return result["code"] + ";" + result["message"]

    def getNodeInfoByType(self, nodeName, sensorType):
        result = ipmi_manager.getNodeInfoByType(nodeName, sensorType)
        if result["code"] == "0":
            return result["code"], result["info"]
        else: 
            return result["code"] + ";" + result["message"]

    def addInstance(self, clusterId, instanceId):
        result = recovery.addInstance(clusterId, instanceId)
        return result["code"]+";"+result["message"]
    
    def deleteInstance(self, clusterId, instanceId):
        result = recovery.deleteInstance(clusterId, instanceId)
        return result["code"]+";"+result["message"]
    
    def listInstance(self, clusterId) :
        result = recovery.listInstance(clusterId)
        if result["code"]== "0":
            return result["code"]+";"+result["instanceList"]
        else:
            return result["code"]+";"+result["message"]
            
    def recoveryVM(self, clusterId, nodeName):
        result = recovery.recoveryVM(clusterId, nodeName)

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

def main():
    
    server = SimpleXMLRPCServer(('',int(config.get("rpc", "rpc_bind_port"))), requestHandler=RequestHandler, allow_none = True, logRequests=False)
    server.register_introspection_functions()
    server.register_multicall_functions()
    server.register_instance(Hass(), allow_dotted_names=True)

    print "HASS Server ready"
    try:
        server.serve_forever()
    except:
        sys.exit(1)
    
if __name__ == "__main__":
    main()
