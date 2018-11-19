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
#	This is a class maintains IPMI command operation
##########################################################


import ConfigParser
import json
import logging
import re
import subprocess
import time

import IPMIConf
from Response import Response


class IPMIManager(object):
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.ip_dict = dict(self.config._sections['ipmi'])
        self.user_dict = dict(self.config._sections['ipmi_user'])

    def rebootNode(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        code = ""
        message = ""
        base = self._baseCMDGenerate(node_name)
        if base is None:
            message = "ipmi node not found , node_name : %s" % node_name
            raise Exception(message)
        try:
            command = base + IPMIConf.REBOOTNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.REBOOTNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is rebooted." % node_name
                logging.info("IpmiModule rebootNode - The Computing Node %s is rebooted." % node_name)
                code = "succeed"
        except Exception as e:
            message = "The Computing Node %s can not be rebooted." % node_name
            logging.error("IpmiModule rebootNode - %s" % str(e))
            code = "failed"
        finally:
            result = Response(code = code,
                              message = message,
                              data = {"node": node_name})
            return result

    def startNode(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        code = ""
        message = ""
        base = self._baseCMDGenerate(node_name)
        if base is None:
            message = "ipmi node not found , node_name : %s" % node_name
            raise Exception(message)
        try:
            command = base + IPMIConf.STARTNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.STARTNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is started." % node_name
                logging.info("IPMIModule startNode - The Computing Node %s is started." % node_name)
                code = "succeed"
        except Exception as e:
            message = "The Computing Node %s can not be started." % node_name
            logging.error("IPMIModule startNode - %s" % str(e))
            code = "failed"
        finally:
            result = Response(code = code,
                              message = message,
                              data = {"node": node_name})
            return result

    def shutOffNode(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        code = ""
        message = ""
        base = self._baseCMDGenerate(node_name)
        if base is None:
            message = "ipmi node not found , node_name : %s" % node_name
            raise Exception(message)
        try:
            command = base + IPMIConf.SHUTOFFNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.SHUTOFFNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is shut down." % node_name
                logging.info("IpmiModule shutOffNode - The Computing Node %s is shut down." % node_name)
                code = "succeed"
        except Exception as e:
            message = "The Computing Node %s can not be shut down." % node_name
            logging.error("IpmiModule shutOffNode - %s" % str(e))
            code = "failed"
        finally:
            result = Response(code = code,
                              message = message,
                              data = {"node": node_name})
            return result

    # for recovery
    def getRecoverInfoByNode(self, node_name, sensor_type):
        """

        :param node_name: 
        :param sensor_type: 
        :return: 
        """
        # vendor = self.config.get("ipmi", "vendor")
        base = self._baseCMDGenerate(node_name)
        if base is None:
            raise Exception("ipmi node not found , node_name : %s" % node_name)
        try:
            command = base + IPMIConf.NODEINFO_BY_TYPE % sensor_type
            # if vendor == "HP":
            #     command += IPMIConf.HP_NODE_CPU_SENSOR_INFO
            # elif vendor == "DELL":
            #     command += IPMIConf.DELL_NODE_CPU_SENSOR_INFO
            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            response, err = p.communicate()
            response = response.split("\n")
            data_list = self._tempDataClean(response)
            return (data_list[0], data_list[1], data_list[2])  # (value,lower_critical,upper_critical)
        except Exception as e:
            message = "Error! Unable to get computing node : %s's hardware information." % node_name
            logging.error("IpmiModule getNodeInfo - %s, %s" % (message, str(e)))
            return "Error"

    def dataClean(self, raw_data):
        """

        :param raw_data: 
        :return: 
        """
        sensor_id = raw_data[1].split(":")[1].strip()
        device = raw_data[2].split(":")[1].strip()
        if device == "7.1":
            device = "System Board"
        elif device == "3.1":
            device = "Processor"
        sensor_type = raw_data[3].split(":")[1].strip()
        value = raw_data[4].split(":")[1].strip()
        status = raw_data[5].split(":")[1].strip()
        lower_critical = raw_data[7].split(":")[1].strip()
        lower = raw_data[8].split(":")[1].strip()
        upper = raw_data[9].split(":")[1].strip()
        upper_critical = raw_data[10].split(":")[1].strip()
        return [sensor_id, device, sensor_type, value, status, lower_critical, lower, upper, upper_critical]

    # for live migration use case
    def _tempDataClean(self, raw_data):
        # sensor_id = raw_data[1].split(":")[1].strip()
        # device = raw_data[2].split(":")[1].strip()
        value = raw_data[4].split(":")[1]
        value = re.findall("[0-9]+", value)[0].strip()  # use regular expression to filter
        lower_critical = raw_data[7].split(":")[1].strip()
        lower_critical = lower_critical.split(".")[0].strip()
        upper_critical = raw_data[10].split(":")[1].strip()
        upper_critical = upper_critical.split(".")[0].strip()
        return [int(value), int(lower_critical), int(upper_critical)]

    def getNodeInfoByType(self, node_name, sensor_type_list):
        """

        :param node_name: 
        :param sensor_type_list: 
        :return: 
        """
        code = ""
        message = ""
        result_list = []
        base = self._baseCMDGenerate(node_name)
        if base is None:
            raise Exception("ipmi node not found , node_name : %s" % node_name)
        for sensor_type in sensor_type_list:
            command = base + IPMIConf.NODEINFO_BY_TYPE % sensor_type
            try:
                p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
                response, err = p.communicate()
                response = response.split("\n")
                # data clean
                sensor_data = self.dataClean(response)
                result_list.append(sensor_data)
                code = "succeed"
                message += "Get computing node : %s's %s information successfully ." % (node_name, sensor_type)
                logging.info("IpmiModule getNodeInfo - " + message)
            except Exception as e:
                message += "Error! Unable to get computing node : %s's %s information." % (
                    node_name, sensor_type)
                logging.error("IpmiModule getNodeInfo - %s" % str(e))
                code = "failed"
        result = Response(code = code,
                          message = message,
                          data = {"info": result_list})
        return result

    def getAllInfoByNode(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        global result
        ipmi_node_sensors_list = json.loads(self.config.get("ipmi_sensor", "ipmi_node_sensors"))
        try:
            result = self.getNodeInfoByType(node_name, ipmi_node_sensors_list)
            logging.info("IPMIModule--getAllInfoByNode finish %s" % result.message)
        except Exception as e:
            message = "IPMIModule--getAllInfoNode fail " + str(e)
            logging.error(message)
            result = Response(code = "failed",
                              message = message,
                              data = {"info": []})
        finally:
            return result

    def getOSStatus(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        interval = (IPMIConf.WATCHDOG_THRESHOLD / 2)
        prev_initial = None
        prev_present = None
        for _ in range(3):
            initial = self._getOSValue(node_name, IPMIConf.OS_TYPE_INITIAL)
            present = self._getOSValue(node_name, IPMIConf.OS_TYPE_PRESENT)
            if initial == False or present == False:
                return "Error"
            if (initial - present) > IPMIConf.WATCHDOG_THRESHOLD:
                return "Error"
            if prev_initial != initial:
                prev_initial = initial
                prev_present = present
                time.sleep(float(interval))
                continue
            if (prev_present - present) < interval:
                return "OK"
            prev_present = present
            time.sleep(float(interval))
        return "Error"

    def _getOSValue(self, node_name, value_type):
        try:
            base = self._baseCMDGenerate(node_name)
            if base is None:
                raise Exception("ipmi node not found , node_name : %s" % node_name)
            command = base + IPMIConf.GET_OS_STATUS
            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            response = p.wait()
            if response != 0:
                raise Exception("Error! The subprocess's command is invalid.")
            while True:
                info = p.stdout.readline()
                if "Stopped" in info:
                    return False
                if not info:
                    break
                if value_type in info:
                    return int(re.findall("[0-9]+", info)[0])  # find value
        except Exception as e:
            logging.error("IPMIModule _getOSValue--" + str(e))
            return False

    def getSensorStatus(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        ipmi_watched_sensor_list = json.loads(self.config.get("ipmi_sensor", "ipmi_watched_sensors"))
        try:
            if self.getPowerStatus(node_name) != "OK":
                return "OK"
            for sensor in ipmi_watched_sensor_list:
                value = self.getRecoverInfoByNode(node_name, sensor)
                if value == "Error":  # node is power off
                    logging.error("get %s sensor value fail" % sensor)
                    return "Error"
                if value[0] > value[2] or value[0] < value[1]:
                    # (value,lower,upper)
                    return "Error"
            return "OK"
        except Exception as e:
            logging.error("IPMIModule-- getSensorStatus fail : %s" % str(e))
            return "Error"

    def getSensorStatusByConfig(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        ipmi_watched_sensor_list = json.loads(self.config.get("ipmi_sensor", "ipmi_watched_sensors"))
        upper_critical = int(self.config.get("ipmi_sensor", "upper_critical"))
        lower_critical = int(self.config.get("ipmi_sensor", "lower_critical"))
        try:
            if self.getPowerStatus(node_name) != "OK":
                return "OK"
            for sensor in ipmi_watched_sensor_list:
                value = self.getRecoverInfoByNode(node_name, sensor)
                if value == "Error":
                    logging.error("get %s sensor value fail" % sensor)
                    return "Error"
                if value[0] > upper_critical or value[0] < lower_critical:
                    return "Error"
            return "OK"
        except Exception as e:
            logging.error("IPMIModule-- getSensorStatusByConfig fail : %s" % str(e))
            return "Error"

    def getPowerStatus(self, node_name):
        """

        :param node_name: 
        :return: 
        """
        status = "OK"
        base = self._baseCMDGenerate(node_name)
        if base is None:
            raise Exception("node not found , node_name : %s" % node_name)
        try:
            command = base + IPMIConf.POWER_STATUS
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.POWER_STATUS_SUCCESS_MSG not in response:
                status = "Error"
                # return status
        except Exception as e:
            logging.error(
                "IpmiModule getPowerStatus - The Compute Node %s's IPMI session can not be established. %s" % (
                    node_name, e))
            status = "IPMI_disable"
        finally:
            return status

    def _baseCMDGenerate(self, node_name):
        if node_name in self.user_dict:
            user = self.user_dict[node_name].split(",")[0]
            passwd = self.user_dict[node_name].split(",")[1]
            cmd = IPMIConf.BASE_CMD % (self.ip_dict[node_name], user, passwd)
            return cmd
        else:
            return None

    def _getIPMIStatus(self, node_name):
        return node_name in self.ip_dict


if __name__ == "__main__":
    i = IPMIManager()
    i.getNodeInfoByType("compute2", ["Inlet Temp"])
    '''
    def getOSStatus(self, node_name):
        status = "OK"
        time.sleep(float(IPMIConf.WATCHDOG_THRESHOLD)) # wait watchdog countdown
        try:
            initial = self._getOSValue(node_name, IPMIConf.OS_TYPE_INITIAL)
            present = self._getOSValue(node_name, IPMIConf.OS_TYPE_PRESENT)
        except Exception as e:
            logging.error("IpmiModule detectOSstatus - %s" % e)
            status = "IPMI_disable"
            return status
        if (initial - present) > IPMIConf.WATCHDOG_THRESHOLD:
            #print initial - present
            status = "Error"
            return status
        else:
            return status

    def resetWatchDog(self, node_name):
        status = True
        base = self._baseCMDGenerate(node_name)
        if base is None:
            # result = {"code": 1}
            result = Response(code="failed")
            return result
        try:
            command = base + IPMIConf.RESET_WATCHDOG
            response = subprocess.check_output(command, shell=True)
            if IPMIConf.WATCHDOG_RESET_SUCEESS_MSG in response:
                logging.info(
                    "IpmiModule resetWatchDog - The Computing Node %s's watchdog timer has been reset." % node_name)
        except Exception as e:
            logging.error("IpmiModule resetWatchDog - %s" % e)
            status = False
        return status
    '''
