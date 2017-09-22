#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import logging
import time
import ConfigParser
import re
import IPMIConf

class IPMIManager(object):  
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.ip_dict = dict(self.config._sections['ipmi'])
        self.user_dict = dict(self.config._sections['ipmi_user'])

    def rebootNode(self, nodeID):
        code = ""
        message = ""
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.REBOOTNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.REBOOTNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is rebooted." % nodeID
                logging.info("IpmiModule rebootNode - The Computing Node %s is rebooted." % nodeID)
                code = "0"
        except Exception as e:
            message = "The Computing Node %s can not be rebooted." % nodeID
            logging.error("IpmiModule rebootNode - %s" % e)
            code = "1"
        finally:
            result = {"code":code, "node":nodeID, "message":message}
            return result

    def startNode(self, nodeID):
        code = ""
        message = ""
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.STARTNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.STARTNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is started." % nodeID
                logging.info("IpmiModule startNode - The Computing Node %s is started." % nodeID)
                code = "0"
        except Exception as e:
            message = "The Computing Node %s can not be started." % nodeID
            logging.error("IpmiModule startNode - %s" % e)
            code = "1"
        finally:
            result = {"code":code, "node":nodeID, "message":message}
            return result
            
    def shutOffNode(self, nodeID):
        code = ""
        message = ""
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.SHUTOFFNODE
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.SHUTOFFNODE_SUCCESS_MSG in response:
                message = "The Computing Node %s is shut down." % nodeID
                logging.info("IpmiModule shutOffNode - The Computing Node %s is shut down." % nodeID)
                code = "0"
        except Exception as e:
            message = "The Computing Node %s can not be shut down." % nodeID
            logging.error("IpmiModule shutOffNode - %s" % e)
            code = "1"
        finally:
            result = {"code":code, "node":nodeID, "message":message}
            return result

    def getAllInfoOfNode(self, nodeID):
        code = ""
        message = ""
        dataList = []
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.NODEINFO
            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            response, err = p.communicate()
            response = response.split("\n")[5:-1]
            dataList = self._dataClean(response)
            code = "0"
            message = "Successfully get computing node : %s's hardware information." % nodeID
            logging.info("IpmiModule getNodeInfo - " + message)
        except Exception as e:
            code = "1"
            message = "Error! Unable to get computing node : %s's hardware information." % nodeID
            logging.error("IpmiModule getNodeInfo - " + err)
        finally:
            result = {"code" : code, "info" : dataList, "message" : message}
            return result

    def _dataClean(self, rawDataList):
        result = []
        for rawData in rawDataList:
            rawData = rawData.split(",")
            value = rawData[1] + " " + rawData[2]
            cleanData = ""
            if "degrees C" in rawData:
                cleanData = [rawData[0], rawData[5], value, rawData[14], rawData[11]]
                result.append(cleanData)
            if "Volts" in rawData:
                cleanData = [rawData[0], rawData[5], value]    
                result.append(cleanData)
        return result

    def getNodeInfoByType(self, nodeID, sensorTypeList):
        code = ""
        message = ""
        resultList = []
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        for sensorType in sensorTypeList:
            sensorData = []
            command = base + IPMIConf.NODEINFO_BY_TYPE % sensorType
            try:
                p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
                response = p.wait()
                if response != 0: # check subprocess's status
                    raise Exception("Error! The subprocess's command is invalid")
	        while True:
	    	    info = p.stdout.readline()
                    if not info:
                        break
                    sensorData.append(info)
                # data clean
                sensorData = self.handleRawData(sensorData, sensorType, nodeID, self.ip_dict[nodeID])
                resultList.append(sensorData)
                code = "0"
                message = message + "Successfully get computing node : %s's %s information." % (nodeID, sensorType)
                logging.info("IpmiModule getNodeInfo - " + message)
	    except Exception as e:
                message = message + "Error! Unable to get computing node : %s's %s information." % (nodeID, sensorType)
                logging.error("IpmiModule getNodeInfo - %s" % e)
                code = "1"
                break
        
        result = {"code":code, "info":result_list, "message":message}
        return result

    def handleRawData(self, rawDataList, sensorType, nodeID, nodeIP):
        result = []
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        for rawData in rawDataList:
            cleanData = [] # to store the data which want to show to user
            # example of rawData: Temp             | 0Eh | ok  |  3.1 | 45 degrees C
            # we wnat to get "Temp"
            sensorID = rawData.split("|")[0].split("  ")[0]  # get sensor ID by rawData
            cleanData.append(sensorID)
            command = base + IPMIConf.RAW_DATA % sensorID
	    try:
	        p = subprocess.Popen(command, stdout = subprocess.PIPE , stderr = subprocess.PIPE, shell=True)
                response = p.wait()
                if response != 0: # check subprocess's status
                    raise Exception("Error! The subprocess's command is invalid")
                    #raise subprocess.CalledProcessError response, command)
                while True:
                    info = p.stdout.readline()
                    if not info:
                        break
                    if 'Sensor Reading' in info or 'Upper critical' in info or 'Lower critical' in info:
                        # use regular expression to find actual data
                        value = re.findall("[0-9\.]+", info)[0]
                        cleanData.append(value)
                    if 'Entity ID' in info:
                        # example data: "Entity ID             : 7.1 (System Board) "
                        # actual need: "System Board"
                        entityID = info.split("(")[-1][:-2]
                        cleanData.append(entityID)
                result.append(cleanData)
            except Exception as e:
                logging.error("IpmiModule handleRawData - %s" % e)
        return result

    def checkOSstatus(self, nodeID):
        initial = 0
        present = 0
        status = "OK"
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.GET_OS_STATUS
            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            response = p.wait()
            if response != 0:
                raise Exception("Error! The subprocess's command is invalid.")
            while True:
                info = p.stdout.readline()
                if not info:
                    break
                if 'Initial Countdown' in info:
                    initial = int(re.findall("[0-9]+", info)[0]) # find value
                if 'Present Countdown' in info:
                    present = int(re.findall("[0-9]+", info)[0]) # find value
            if (initial - present) > IPMIConf.WATCHDOG_THRESHOLD:
                #print initial - present
                status = "Error"
                return status
            else:
                return status
        except Exception as e:
            logging.error("IpmiModule detectOSstatus - %s" % e)
            status = "IPMI_disable"
            return status

    def checkSensorStatus(self, nodeID):
        status = "OK"
        failureTempList = []
        failureVoltList = []
        base = self._baseCMDGenerate(nodeID)
        if command is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.SENSOR_STATUS
            p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell=True)
            response, err = p.communicate()
            response = response.split("\n")[5:-1]
            status, failureTempList, failureVoltList = self._checkValue(response)
        except Exception as e:
            logging.error("IpmiModule checkSensorStatus - " + e)
            status = "IPMI_disable"
        return status, failureTempList, failureVoltList
    
    def _checkValue(self, rawDataList):
        status = "OK"
        failureTemp = []
        failureVolt = []
        for rawData in rawDataList:
            rawData = rawData.split(",")
            if rawData[1]: # has sensor value 
                value = float(rawData[1])
                upperThreshold = float(rawData[11]) if rawData[11] else value
                lowerThreshold = float(rawData[14]) if rawData[14] else value
                if "degrees C" in rawData:
                    if value > upperThreshold:
                        failureTemp.append((rawData[0],"upper"))
                        status = "Error"
                    elif value < lowerThreshold:
                        failureTemp.append((rawData[0],"lower"))
                        status = "Error"
                if "Volts" in rawData:
                    if value > upperThreshold:
                        failureVolt.append((rawData[0],"upper"))
                        status = "Error"
                    elif value < lowerThreshold:
                        failureVolt.append((rawData[0],"lower"))
                        status = "Error"
        return status, failureTemp, failureVolt

    def resetWatchDog(self, nodeID):
        status = True
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.RESET_WATCHDOG
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.WATCHDOG_RESET_SUCEESS_MSG in responese:
                logging.info("IpmiModule resetWatchDog - The Computing Node %s's watchdog timer has been reset." % nodeID)
        except Exception as e:
            logging.error("IpmiModule resetWatchDog - %s" % e)
            status = False
        return status

    def checkPowerStatus(self, nodeID):
        status = "OK"
        base = self._baseCMDGenerate(nodeID)
        if base is None:
            result = {"code" : 1}
            return result
        try:
            command = base + IPMIConf.POWER_STATUS
            response = subprocess.check_output(command, shell = True)
            if IPMIConf.POWER_STATUS_SUCCESS_MSG not in response:
                status = "Error"
            return status
        except Exception as e:
            logging.error("IpmiModule checkPowerStatus - The Compute Node %s's IPMI session can not be established." % nodeID )
            status = "IPMI_disable"
        return status

    def _baseCMDGenerate(self, nodeID):
        if nodeID in self.user_dict:
            user = self.user_dict[nodeID].split(",")[0]
            passwd = self.user_dict[nodeID].split(",")[1]
            cmd = IPMIConf.IPMI_BASE_CMD % (self.ip_dict[nodeID] , user , passwd)
            return cmd
        else:
            return None
