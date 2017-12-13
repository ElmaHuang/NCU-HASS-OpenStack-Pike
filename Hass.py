#!/usr/bin/python
#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   HASS Service
#   Using SimpleXMLRPC library handle http requests
#   Client can use function in Hass class directly
##########################################################


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from base64 import b64decode
import ConfigParser
import logging
import os
import sys

from RecoveryManager import RecoveryManager
from ClusterManager import ClusterManager
from IPMINodeOperator import Operator

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
                logging.info("Hass RequestHandler - Authentication success, request from %s", self.clientip)
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
    def __init__(self):
        ClusterManager.init()
        self.Operator = Operator()
        self.RecoveryManager = RecoveryManager()

    def test_auth_response(self):
    #Unit tester call this function to get successful message if authenticate success.
        return "auth success"
        
    def createCluster(self, name, nodeList=[]):
        try:
            createCluster_result = ClusterManager.createCluster(name)
            if createCluster_result["code"] == "0":
                if nodeList != []:
                    addNode_result = ClusterManager.addNode(createCluster_result["clusterId"], nodeList)

                    if addNode_result["code"] == "0":
                        message = "Create HA cluster and add computing node success, cluster uuid is %s , add node message %s" % (createCluster_result["clusterId"], addNode_result["message"])
                        logging.info(message)
                        result= {"code" : "0","message": message}
                        return result
                    else:
                        #add node fail
                        message = "The cluster is created.(uuid = " + createCluster_result["clusterId"] + ") But," + addNode_result["message"]
                        logging.error(message)
                        result ={"code":"0","message":message}
                        return result
                else :#nodelist is None
                    #addNode_result = {"code":"0", "clusterId":createCluster_result["clusterId"], "message":"not add any node."}
                    logging.info(createCluster_result["message"])
                    return createCluster_result
            else:
                #create cluster
                logging.error("HASS-create cluster--create cluster fail")
                return createCluster_result
        except:
            logging.error("HASS-create cluster-except--create cluster fail")

    def deleteCluster(self, cluster_uuid):
        try:
            result = ClusterManager.deleteCluster(cluster_uuid)
            return result
        except:
            logging.error("HASS--delete cluster fail")

    def listCluster(self):
        try:
            result = ClusterManager.listCluster()
            return result
        except:
            logging.error("HASS--list all cluster fail")

    def addNode(self, clusterId, nodeList):
        try:
            result = ClusterManager.addNode(clusterId, nodeList)
            return result
        except:
            logging.error("HASS--add node fail")

    def deleteNode(self, cluster_id, node_name):
        try:
            result = ClusterManager.deleteNode(cluster_id, node_name)
            return result
        except:
            logging.error("HASS--delete node fail")

    def listNode(self, clusterId) :
        try:
            result = ClusterManager.listNode(clusterId)
            return result
        except:
            logging.error("HASS--List node fail")

    def startNode(self, nodeName):
        try:
            result = self.Operator.startNode(nodeName)
            return result
        except:
            logging.error("HASS--Start node fail")

    def shutOffNode(self, nodeName):
        try:
            result = self.Operator.shutOffNode(nodeName)
            return result
        except:
            logging.error("HASS--Shut off fail")

    def rebootNode(self, nodeName):
        try:
            result = self.Operator.rebootNode(nodeName)
            return result
        except:
            logging.error("HASS--reboot node fail")

    def getAllInfoOfNode(self, nodeName):
        try:
            result = self.Operator.getAllInfoByNode(nodeName)
            logging.info("HASS--get All Info from %s finish" %nodeName)
            return result
        except:
            logging.error("HASS--get All Info from %s fail"%nodeName)

    def getNodeInfoByType(self, nodeName, sensorType):
        try:
            result = self.Operator.getNodeInfoByType(nodeName, sensorType)
            logging.info("HASS--get %s info from %s success"%(sensorType,nodeName))
            return result
        except:
            logging.error("HASS--get %s info from %s fail" %(sensorType,nodeName))

    def addInstance(self, clusterId, instanceId):
        try:
            result = ClusterManager.addInstance(clusterId, instanceId)
            logging.info("HASS--add instance success.")
            return result
        except:
            logging.error("HASS--add Instance fail")

    def deleteInstance(self, clusterId, instanceId):
        try:
            result = ClusterManager.deleteInstance(clusterId, instanceId)
            logging.info("HASS--delete instance success")
            return result
        except:
            logging.error("HASS--delete instance fail")

    def listInstance(self, clusterId) :
        try:
            result = ClusterManager.listInstance(clusterId)
            logging.info("HASS-list instance success")
            return result
        except :
            logging.error("HASS--list instance fail")
    
    def recover(self, fail_type, cluster_id, node_name):
        try:
            result = self.RecoveryManager.recover(fail_type, cluster_id, node_name)
            return result
        except Exception as e:
            print str(e)
            logging.error("HASS--recover node %s fail" % node_name)

def main():
    config = ConfigParser.RawConfigParser()
    config.read('hass.conf')

    log_level = logging.getLevelName(config.get("log", "level"))
    log_file_name = config.get("log", "location")
    dir = os.path.dirname(log_file_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    logging.basicConfig(filename=log_file_name, level=log_level, format="%(asctime)s [%(levelname)s] : %(message)s")

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
