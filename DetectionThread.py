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


ipmi_manager = IPMIManager()

HEALTH = "health"
NETWORK_FAIL = "network"
SERVICE_FAIL = "service"
POWER_FAIL = "power"
SENSOR_FAIL = "sensor"
OS_FAIL = "os"



class DetectionThread(threading.Thread):
    def __init__(self, interval, threshold, clusterId, node, port, restart_threshold, ipmi_status):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.threshold = int(threshold) # error threshold
        self.restart_threshold = int(restart_threshold) # not used
        self.interval = float(interval) # actual polling interval
        self.default_interval = self.interval # initial interval
        self.clusterId = clusterId
        self.node = node
        self.port = port
        self.exit = False
        self.recovery_flag = True
        self.service_failure_data = ""
        #status index represent --
        #0 = network
        #1 = libvirt,QEMU/KVM
        #2 = power
        #3 = os
        #4 = sensor(temperature, voltage)
        self.state_list = [0,0,0,0,0]
        self.ipmi_status = ipmi_status
        self.config = ConfigParser.RawConfigParser()
        self.config.read('failureTable.conf')
        self.failure_code = dict(self.config._sections['failure_code'])
        self.function_map = [self.checkPowerStatus, self.checkOSStatus, self.checkNetworkStatus, self.checkServiceStatus]

    def run(self):
        data = ""
        failure_occured_time = 0
        failure_detection_time = 0
        #connect to FA
        try:
            print "["+self.node+"] create socket connection"
            self.sock.settimeout(0.5)
            self.sock.connect((self.node, self.port))
            time.sleep(5)
        except:
            print "Init ["+self.node+"] connection failed"
        while not self.exit:

            state = self.detect()
            print state

            """
            #if error has been detected, then shorten the detection interval time 
            if sum(self.state_list) > 0 and all(state <2 for state in self.state_list) and self.interval == self.default_interval:
                self.interval = self.default_interval / 2
                check_code = "".join(str(state) for state in self.state_list) # to check failure occurs in cycle or not
                failure_occured_time = time.time()
                #if check_code not in self.failure_code: # failure occered in failure cycle may lead to misjugde
                self.state_list = [0] * 5
            elif sum(self.state_list) > 0:
                pass
            else:
                self.interval = self.default_interval
            
            #check if any state value over threshold
            #print self.node, "'s state is ", self.state_list

            if self.threshold in self.state_list:
                failure_detection_time = time.time() - failure_occured_time
                print "Failure detection time : ", failure_detection_time
                # reset other value which small than threshold
                state_list = [state / self.threshold if state == self.threshold else 0 for state in self.state_list] 

                #recovery
                result_code = "".join(str(state) for state in state_list)
                if result_code in self.failure_code:
                    # get failure type and call corresponding function
                    recovery_type = self.failure_code[result_code]
                    print "Failure : ", recovery_type, " has occured!"

                    # to determine whether exit thread or not
                    self.recovery_flag = recovery_function[recovery_type](self.clusterId, self.node, self.service_failure_data)
                    if self.recovery_flag:
                        logging.info("DetectionManager PollingThread - The %s failed but recovery successfully")
                        self.state_list = [0] * 5
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.sock.setblocking(0)
                        self.sock.settimeout(0.5)
                        self.sock.connect((self.node, self.port))
                        self.ipmi_status = True
                    else:
                        server.removeNodeFromCluster(self.clusterId, self.node)
                        self.exit = True
                else:
                    logging.error("DetectionManager PollingThread - The %s has unknown failure so removed from cluster" % self.node)

                    server.recoveryVM(self.clusterId, self.node)
                    server.removeNodeFromCluster(self.clusterId, self.node)
                    self.exit = True
            else:
                time.sleep(self.interval)
        """
                
    def stop(self):
        self.exit = True
    
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


    def detect(self):
        for _ in self.function_map:
            state = _()
            if state == HEALTH:
                continue
            else:
                return self.verify(_)
        return HEALTH

    def verify(self, func):
        index = self.function_map.index(func)
        reversed_function_map = self.function_map[:]
        reversed_function_map = reversed_function_map[0:index+1]
        reversed_function_map.reverse()

        #print reversed_function_map

        fail = None
        for _ in reversed_function_map:
            state = _()
            if state == HEALTH and _ == func:
                return HEALTH
            elif state == HEALTH:
                return fail
            elif not state == HEALTH:
                fail = state
        return fail

    def checkNetworkStatus(self):
        try:
            response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', self.node], stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError:
            return NETWORK_FAIL
        return HEALTH

    def checkServiceStatus(self):
        try:
            line = "polling request"
            self.sock.sendall(line)
            data, addr = self.sock.recvfrom(1024)
            if data == "OK":
                return HEALTH
                print "["+self.node+"] OK" 
            elif "error" in data :
                print data
                print "["+self.node+"]service Failed"
            elif not data:
                print "["+self.node+"]no ACK"
            else:
                 print "["+self.node+"]Receive:"+data   
            return SERVICE_FAIL
        except Exception as e:
                print "["+self.node+"] connection failed"
                self.sock.connect((self.node, self.port))
                return SERVICE_FAIL

    def checkPowerStatus(self):
        status = ipmi_manager.getPowerStatus(self.node)
        if status == "OK":
            return HEALTH
        return POWER_FAIL

    def checkOSStatus(self):
        status = ipmi_manager.getOSStatus(self.node)
        if status == "OK":
            return HEALTH
        return OS_FAIL

    def checkSensorStatus(self):
        status = ipmi_manager.getSensorStatus(self.node)
        if status == "OK":
            return HEALTH
        return SENSOR_FAIL