#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains IPMI command operation.
##########################################################

# from NovaClient import NovaClient
from IPMIModule import IPMIManager
from ClusterManager import ClusterManager
from Response import Response
import time
import ConfigParser
import logging
import socket


class Operator(object):
    def __init__(self):
        # self.nova_client = NovaClient.getInstance()
        self.ipmi_module = IPMIManager()
        self.cluster_list = ClusterManager.getClusterList()
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.port = int(self.config.get("detection", "polling_port"))

    def startNode(self, node_name, default_wait_time=180):
        message = ""
        data = {"node_name": node_name}
        result = None
        try:
            if self._checkNodeIPMI(node_name):
                message += " IPMIOperator--node is in compute pool . The node is %s." % node_name
                ipmi_result = self.ipmi_module.startNode(node_name)
                if ipmi_result.code == "succeed":
                    boot_up = self._checkNodeBootSuccess(node_name, default_wait_time)
                    if boot_up:
                        message += "start node success.The node is %s." % node_name
                        detection = self._checkDetectionAgent(node_name, default_wait_time)
                        if not detection:
                            message += "detectionagent in computing node is fail."
                        message += "detectionagent in computing is runnung!"
                        result = self.successResult(message, data)
                        logging.info(message)
                        # result = Response(code="succeed", message=message, data={"node_name": node_name})
                    else:
                        # boot_up is fail
                        message += "check node boot fail"
                        result = self.failResult(message, data)
                        logging.error(message)
                else:
                    # ipmi_result is fail
                    message += "IpmiModule start node fail"
                    result = self.failResult(message, data)
                    logging.error(message)
            else:
                # node is not ipmi node
                message += " IPMIOperator--node is not in compute pool or is not a IPMI PC . The node is %s." % node_name
                result = self.failResult(message, data)
                logging.error(message)
                # result = Response(code="failed", message=message, data={"node_name": node_name})
        except Exception as e:
            message += "IPMIOperator--start node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed", message=message, data={"node_name": node_name})
        finally:
            return result

    def shutOffNode(self, node_name):
        message = ""
        data = {"node_name": node_name}
        result = None
        try:
            if self._checkNodeIPMI(node_name) and self._checkNodeNotInCluster(node_name):
                ipmi_result = self.ipmi_module.shutOffNode(node_name)
                # check power status in IPMIModule
                if ipmi_result.code == "succeed":
                    message += "shut off node success.The node is %s." % node_name
                    result = self.successResult(message, data)
                    logging.info(message)
                    # result = Response(code="succeed", message=message, data={"node_name": node_name})
                else:
                    message += "IpmiModule shut off node fail"
                    result = self.failResult(message, data)
                    logging.error(message)
            else:
                message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
                result = self.failResult(message, data)
                logging.error(message)
                # result = Response(code="failed", message=message, data={"node_name": node_name})
        except Exception as e:
            # shut off fail
            message += "IPMIOperator--shut off node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed", message=message, data={"node_name": node_name})
        finally:
            return result

    def rebootNode(self, node_name, default_wait_time=180):
        result = None
        data = {"node_name": node_name}
        message = ""
        try:
            if self._checkNodeIPMI(node_name) and self._checkNodeNotInCluster(node_name):
                ipmi_result = self.ipmi_module.rebootNode(node_name)
                if ipmi_result.code == "succeed":
                    message += "reboot node success.The node is %s." % node_name
                    detection = self._checkDetectionAgent(node_name, default_wait_time)
                    if not detection:
                        message += "detectionagent in computing node is fail."
                    message += "detectionagent in computing is runnung!"
                    result = self.successResult(message, data)
                    logging.info(message)
                    # result = Response(code="succeed", message=message, data={"node_name": node_name})
                else:
                    message += "IpmiModule reboot node fail"
                    result = self.failResult(message, data)
                    logging.error(message)
            else:
                message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
                result = self.failResult(message, data)
                logging.error(message)
                # result = Response(code="failed", message=message, data={"node_name": node_name})
        except Exception as e:
            # shut off fail
            message += "IPMIOperator--reboot node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
            # result = Response(code="failed", message=message, data={"node_name": node_name})
        finally:
            return result

    def getAllInfoByNode(self, node_name):
        try:
            data = self.ipmi_module.getAllInfoByNode(node_name)
            return data
        except Exception as e:
            logging.error("IPMIOperator get all sensor info of node fail.%s" % str(e))

    def getNodeInfoByType(self, node_name, sensor_type):
        try:
            data = self.ipmi_module.getNodeInfoByType(node_name, sensor_type)
            return data
        except Exception as e:
            logging.error("IPMIOperator get %s sensor info of node fail.%s" % (sensor_type, str(e)))

    def _checkNodeIPMI(self, node_name):
        # is IPMI PC
        ipmistatus = self.ipmi_module._getIPMIStatus(node_name)
        if not ipmistatus:
            return False
        # is in computing pool
        if ClusterManager.nova.isInComputePool(node_name):
            message = " node is in compute pool . The node is %s." % node_name
            logging.info(message)
            return True
        else:
            message = " node is not in compute pool please check again! The node is %s." % node_name
            logging.error(message)
            return False

    def _checkNodeNotInCluster(self, node_name):
        for cluster_id in self.cluster_list:
            cluster = ClusterManager.getCluster(cluster_id)
            node_list = cluster.getAllNodeStr()
            if node_name in node_list:
                return False
        return True

    def _checkNodeBootSuccess(self, nodeName, check_timeout):
        # check power statue in IPMIModule
        status = False
        while not status:
            if check_timeout > 0:
                result = self.ipmi_module.getPowerStatus(nodeName)
                print result, check_timeout
                if result == "OK":
                    status = True
                else:
                    time.sleep(1)
                    check_timeout -= 1
            else:
                return status
        return status

    def _checkDetectionAgent(self, nodeName, check_timeout):
        # not be protect(not connect socket)
        # check detection agent
        status = False
        data = ""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(0)
            sock.settimeout(0.5)
            sock.connect((nodeName, self.port))
        except Exception as e:
            print "create socket fail", str(e)

        while not status:
            time.sleep(5)
            if check_timeout > 0:
                try:
                    sock.sendall("polling request")
                    data, addr = sock.recvfrom(2048)
                except Exception as e:
                    print str(e)

                if "OK" in data:
                    status = True
                    sock.close()
                    # print data
                else:
                    # time.sleep(1)
                    print "wating:", check_timeout
                    check_timeout -= 5
            else:
                # timeout
                return status
        # status is True
        return status

    def successResult(self, message, data):
        result = Response(code="succeed",
                          message=message,
                          data=data)
        return result

    def failResult(self, message, data):
        result = Response(code="failed",
                          message=message,
                          data=data)
        return result
