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


import ConfigParser
import logging
import socket
import time

from ClusterManager import ClusterManager
# from NovaClient import NovaClient
from IPMIModule import IPMIManager
from Response import Response


class Operator(object):
    def __init__(self):
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
            if self._checkNodeIPMI(node_name) and self._checkNodeInComputePool(node_name):
                message += " IPMIOperator--node is in compute pool . The node is %s." % node_name
                ipmi_result = self.ipmi_module.startNode(node_name)
                if ipmi_result.code == "succeed":
                    boot_up = self._checkNodeBootSuccess(node_name, default_wait_time)
                    if boot_up:
                        message += "start node success.The node is %s." % node_name
                        detection = self._checkDetectionAgent(node_name, default_wait_time)
                        if not detection:
                            message += "DetectionAgent in computing node is fail."
                        message += "DetectionAgent in computing is running!"
                        result = self.successResult(message, data)
                        logging.info(message)
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
        except Exception as e:
            message += "IPMIOperator--start node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
        finally:
            return result

    def shutOffNode(self, node_name):
        message = ""
        data = {"node_name": node_name}
        result = None
        try:
            if self._checkNodeIPMI(node_name) and self._checkNodeInComputePool(
                    node_name) and self._checkNodeNotInCluster(node_name):
                ipmi_result = self.ipmi_module.shutOffNode(node_name)
                # check power status in IPMIModule
                if ipmi_result.code == "succeed":
                    message += "shut off node success.The node is %s." % node_name
                    result = self.successResult(message, data)
                    logging.info(message)
                else:
                    message += "IpmiModule shut off node fail"
                    result = self.failResult(message, data)
                    logging.error(message)
            else:
                message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
                result = self.failResult(message, data)
                logging.error(message)
        except Exception as e:
            # shut off fail
            message += "IPMIOperator--shut off node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
        finally:
            return result

    def rebootNode(self, node_name, default_wait_time=180):
        result = None
        data = {"node_name": node_name}
        message = ""
        try:
            if self._checkNodeIPMI(node_name) and self._checkNodeInComputePool(
                    node_name) and self._checkNodeNotInCluster(node_name):
                ipmi_result = self.ipmi_module.rebootNode(node_name)
                if ipmi_result.code == "succeed":
                    message += "reboot node success.The node is %s." % node_name
                    detection = self._checkDetectionAgent(node_name, default_wait_time)
                    if not detection:
                        message += "DetectionAgent in computing node is fail."
                    message += "DetectionAgent in computing is running!"
                    result = self.successResult(message, data)
                    logging.info(message)
                else:
                    message += "IpmiModule reboot node fail"
                    result = self.failResult(message, data)
                    logging.error(message)
            else:
                message += " IPMIOperator--node is not in compute pool or is not a IPMI PC or is already be protected. The node is %s." % node_name
                result = self.failResult(message, data)
                logging.error(message)
        except Exception as e:
            message += "IPMIOperator--reboot node fail.The node is %s.%s" % (node_name, str(e))
            result = self.failResult(message, data)
            logging.error(message)
        finally:
            return result

    def getAllInfoByNode(self, node_name):
        try:
            result = self.ipmi_module.getAllInfoByNode(node_name)
        except Exception as e:
            message = " IPMIOperator--get node info bt type fail. The node is %s." % node_name
            result = self.failResult(message, [])
            logging.error("IPMIOperator get all sensor info of node fail.%s" % str(e))
        finally:
            return result

    def getNodeInfoByType(self, node_name, sensor_type):
        try:
            result = self.ipmi_module.getNodeInfoByType(node_name, sensor_type)
        except Exception as e:
            message = " IPMIOperator--get node info bt type fail. The node is %s,sensor type is %s ." % (
                node_name, sensor_type)
            result = self.failResult(message, [])
            logging.error("IPMIOperator get %s sensor info of node fail.%s" % (sensor_type, str(e)))
        finally:
            return result

    def _checkNodeIPMI(self, node_name):
        ipmistatus = self.ipmi_module._getIPMIStatus(node_name)
        if not ipmistatus:
            message = " Node is not IPMI PC please check again! The node is %s." % node_name
            logging.error(message)
        else:
            message = " Node is IPMI PC. node is %s." % node_name
            logging.info(message)
        return ipmistatus

    def _checkNodeInComputePool(self, node_name):
        result = ClusterManager.nova.isInComputePool(node_name)
        if result:
            message = " Node is in compute pool . The node is %s." % node_name
            logging.info(message)
        else:
            message = " Node is not in compute pool please check again! The node is %s." % node_name
            logging.error(message)
        return result

    def _checkNodeNotInCluster(self, node_name):
        result = True
        if self.cluster_list is None:
            pass
        else:
            for cluster_id, cluster in self.cluster_list.iteritems():
                node_list = cluster.getAllNodeStr()
                if node_name in node_list:
                    logging.error(" Node is in HA cluster. The node is %s, cluster id is %s" % (node_name, cluster_id))
                    result = False
        return result

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
                else:
                    # time.sleep(1)
                    print "waiting:", check_timeout
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
