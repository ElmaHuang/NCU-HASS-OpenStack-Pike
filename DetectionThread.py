import socket
import sys
import threading
import time
import logging
import ConfigParser
import argparse
import xmlrpclib
import subprocess
import json
import copy
from IPMIModule import IPMIManager

class DetectionThread(threading.Thread):
    def __init__(self, interval, threshold, clusterId, node, port, restart_threshold, ipmi_status):
        threading.Thread.__init__(self)
        self.node = node
        self.port = port
        self.clusterId = clusterId
        self.ipmi_status = ipmi_status
        self.exit_detect = False
        self.config = ConfigParser.RawConfigParser()
        self.config.read('failureTable.conf')
        self.detect = Detect_Case(self.node,self.port,self.ipmi_status)
        self.function_map = [self.detect.checkPowerStatus, self.detect.checkOSStatus, self.detect.checkNetworkStatus, self.detect.checkServiceStatus]
        self.authUrl = "http://" + self.config.get("rpc", "rpc_username") + ":" + self.config.get("rpc","rpc_password") + "@127.0.0.1:" + self.config.get("rpc", "rpc_bind_port")
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        self.interval = float(interval) # actual polling interval

        self.threshold = int(threshold) # error threshold
        self.restart_threshold = int(restart_threshold) # not used
        self.default_interval = self.interval # initial interval
        self.recovery_flag = True
        self.service_failure_data = ""
        #status index represent --
        #0 = network
        #1 = libvirt,QEMU/KVM
        #2 = power
        #3 = os
        #4 = sensor(temperature, voltage)
        self.state_list = [0,0,0,0,0]
        self.failure_code = dict(self.config._sections['failure_code'])

    def run(self):
        data = ""
        failure_occured_time = 0
        failure_detection_time = 0
        #connect to FA
        self.detect._sockect_connect()
        while not self.exit_detecte:
            time.sleep(self.interval)
            state = self.detect_loop()
            print "["+ self.node.name + "] " + state

            if state != Status.HEALTH:
                print state
                try:
                    pass
                    #call case in recovery map
                except Exception as e:
                    print e
                    self.stop()

    def detect_loop(self):
        for case in self.function_map:
            state = case()
            if state == Status.HEALTH:
                continue
            else:
                return self.verify(case,state)
        return Status.HEALTH

    def verify(self, func,state):
        self.state=state
        self.index = self.function_map.index(func)
        #eg :func = network fail
        reversed_function_map = self.function_map[:]#reversed_function=[Power,OS.Network,Service]
        reversed_function_map = reversed_function_map[0:self.index+1]#reversed_function = [Power,OS,Network]
        reversed_function_map.reverse()#reversed_function = [Network,OS,Power]

        #print reversed_function_map
        fail_string = self.state
        for fail in reversed_function_map:
            check_state = fail()
            if check_state == Status.HEALTH and fail == func:
                #Network is health and network is func
                return Status.HEALTH
                #return network is fail
            elif check_state == Status.HEALTH:
                #OS is health ,OS is not func
                return fail_string
                #return network is fail
            elif not check_state == Status.HEALTH:
                fail_string = state #OS
        return fail_string

    def stop(self):
        self.exit_detecte = True
    
    def print_critical_sensor(self, critical_sensor, type):
        message = ""
        upper_list = []
        lower_list = []
        for sensor in critical_sensor:
            if sensor[1] == 'upper':
                upper_list.append(sensor[0])
            else:
                lower_list.append(sensor[0])
        if len(upper_list) != 0:
            message = message + "Sensor : " + ",".join(upper_list) + "'s " + type + " is too high.\n"
        if len(lower_list) != 0:
            message = message + "Sensor : " + ",".join(upper_list) + "'s" + type + " is too low.\n"
        print message

class Detect_Case():

    def __init__(self,node_name,port,ipmi_status):
        self.ipmi_manager = IPMIManager()
        self.ipmi_status = ipmi_status
        self.port=port
        self.node = node_name

    #3
    def checkNetworkStatus(self):
        try:
            response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', self.node], stderr=subprocess.STDOUT, universal_newlines=True)
            return Status.HEALTH
        except subprocess.CalledProcessError:
            return Status.NETWORK_FAIL
    #4
    def checkServiceStatus(self):
        try:
            line = "polling request"
            self.sock.sendall(line)
            data, addr = self.sock.recvfrom(1024)
            if data == "OK":
                print "[" +self.node +"] OK"
                return Status.HEALTH

            elif "error" in data :
                print data
                print "["+self.node+"]service Failed"

            elif not data:
                print "["+self.node+"]no ACK"

            else:
                 print "["+self.node+"]Receive:"+data

            return Status.SERVICE_FAIL

        except Exception as e:
                print "["+self.node+"] connection failed"
                print e
                self.sock.connect((self.node, self.port))
                return Status.SERVICE_FAIL
    #1
    def checkPowerStatus(self):
        status = self.ipmi_manager.getPowerStatus(self.node)
        if status == "OK":
            return Status.HEALTH
        return Status.POWER_FAIL
    #2
    def checkOSStatus(self):
        status = self.ipmi_manager.getOSStatus(self.node)
        if status == "OK":
            return Status.HEALTH
        return Status.OS_FAIL

    def checkSensorStatus(self):
        status = self.ipmi_manager.getSensorStatus(self.node)
        if status == "OK":
            return Status.HEALTH
        return Status.SENSOR_FAIL

    def _sockect_connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        try:
            print "["+self.node+"] create socket connection"
            self.sock.settimeout(0.5)
            self.sock.connect((self.node, self.port))
            time.sleep(5)
        except:
            print "Init ["+self.node+"] connection failed"
class Status():

    HEALTH = "health"
    NETWORK_FAIL = "network"
    SERVICE_FAIL = "service"
    POWER_FAIL = "power"
    SENSOR_FAIL = "sensor"
    OS_FAIL = "os"

if __name__ == '__main__':
    DetectionThread()