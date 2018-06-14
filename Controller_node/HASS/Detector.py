#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#	This is a class which contains detect functions.
##########################################################


from __future__ import print_function

import ConfigParser
import logging
import socket
import subprocess
import time

import State
from IPMIModule import IPMIManager


class Detector(object):
    def __init__(self, node, port):
        self.node = node.name
        self.ipmi_status = node.ipmi_status
        self.ipmi_manager = IPMIManager()
        self.port = port
        self.sock = None
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.connect()

    def connect(self):
        # connect to FA
        try:
            print("[" + self.node + "] create socket connection")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(0)
            self.sock.settimeout(0.5)
            self.sock.connect((self.node, self.port))
        except Exception as e:
            print(str(e))
            print("Init [" + self.node + "] connection failed")

    def checkNetworkStatus(self):
        heartbeat_time = int(self.config.get("default", "heartbeat_time"))
        network_fail = False
        while heartbeat_time > 0:
            try:
                response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', self.node],
                                                   stderr = subprocess.STDOUT, universal_newlines = True)
                network_fail = False
            except Exception as e:
                logging.error("transient network fail" + str(e))
                fail = True
                pass
            finally:
                time.sleep(1)
                heartbeat_time -= 1
        if not network_fail:
            return State.HEALTH
        return State.NETWORK_FAIL

    def checkServiceStatus(self):
        try:
            line = "polling request"
            self.sock.sendall(line)
            data, addr = self.sock.recvfrom(1024)
            if data == "OK":
                return State.HEALTH
            elif "error" in data:
                print(data)
                print("[" + self.node + "]service Failed")
            elif not data:
                print("[" + self.node + "]no ACK")
            else:
                print("[" + self.node + "]Receive:" + data)
            return State.SERVICE_FAIL
        except Exception as e:
            # fail_services = "agents"
            logging.error("Detector checkServiceStatus Except:" + str(e))
            print("[" + self.node + "] connection failed")
            self.sock.connect((self.node, self.port))
            return State.SERVICE_FAIL

    def checkPowerStatus(self):
        if not self.ipmi_status:
            return State.HEALTH
        status = self.ipmi_manager.getPowerStatus(self.node)
        if status == "OK":
            return State.HEALTH
        return State.POWER_FAIL

    def checkOSStatus(self):
        if not self.ipmi_status:
            return State.HEALTH
        status = self.ipmi_manager.getOSStatus(self.node)
        if status == "OK":
            return State.HEALTH
        return State.OS_FAIL

    def checkSensorStatusByConfig(self):
        if not self.ipmi_status:
            return State.HEALTH
        print("get hass sensor setting:", time.time())
        status = self.ipmi_manager.getSensorStatusByConfig(self.node)
        if status == "OK":
            return State.HEALTH
        print("sensor config fail")
        return State.SENSOR_CONFIG_FAIL

    def checkSensorStatus(self):
        if not self.ipmi_status:
            return State.HEALTH
        status = self.ipmi_manager.getSensorStatus(self.node)
        if status == "OK":
            return State.HEALTH
        return State.SENSOR_FAIL

    def getFailServices(self):
        try:
            line = "polling request"
            self.sock.sendall(line)
            data, addr = self.sock.recvfrom(1024)
            if data != "OK":
                return data
            return None
        except Exception as e:
            logging.error("Detector getFailServices--Except :" + str(e))
            return "agents"
