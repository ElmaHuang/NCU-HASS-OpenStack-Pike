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
from IPMIModule import IPMIManager
ipmi_manager = IPMIManager()

server_config = ConfigParser.RawConfigParser()
server_config.read('hass.conf')
authUrl = "http://"+server_config.get("rpc", "rpc_username")+":"+server_config.get("rpc", "rpc_password")+"@127.0.0.1:"+server_config.get("rpc", "rpc_bind_port")
server = xmlrpclib.ServerProxy(authUrl)

# failure recovery table
recovery_function = {"sensor_value_critical" : server.recoveryByShutOffNode,
                     "sensor_value_critical_and_service_failure" : server.recoveryByShutOffNode,
                     "sensor_value_critical_and_os_hanged" : server.recoveryByShutOffNode,
                     "sensor_valure_critical_and_host_network_failure" : server.recoveryByShutOffNode,
                     "host_crash" : server.recoveryByShutOffNode,
                     "service_failure" : server.recoveryServiceFailure,
                     "ipmi_daemon_failure" : server.recoveryIPMIDaemonFailure,
                     "watchdog_daemon_failure" : server.recoveryWatchdogDaemonFailure,
                     "os_hanged" : server.recoveryOSHanged,
                     "host_network_failure" : server.recoveryNetworkFailure,
                     "power_off" : server.recoveryPowerOff}

class DetectionManager():

    def __init__(self) :
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.threadList = []
        self.ipmi_IP_dict = dict(self.config._sections['ipmi'])

    def pollingRegister(self, id, node, test):
        ipmi_status = True
        if node not in self.ipmi_IP_dict:
            ipmi_status = False
        nodeInfo = {"id":id, "node":node, "thread":PollingThread(self.config.get("detection","polling_interval"), self.config.get("detection","polling_threshold"), id, node, int(self.config.get("detection","polling_port")), int(self.config.get("detection","wait_restart_threshold")), ipmi_status, test)}
        self.threadList.append(nodeInfo)
        try:
            nodeInfo["thread"].daemon=True
            nodeInfo["thread"].start()
        except (KeyboardInterrupt, SystemExit):
            print '\n! Received keyboard interrupt, quitting threads.\n'
        
    def pollingCancel(self, id, node):
        newthreadList = []
        for nodeInfo in self.threadList:
            if nodeInfo["id"] == id and nodeInfo["node"]==node :                
                try:
                    nodeInfo["thread"].stop()
                except:
                    pass
            else :
                newthreadList.append(nodeInfo)
        self.threadList = newthreadList

class PollingThread(threading.Thread):
    def __init__(self, interval, threshold, clusterId, node, port, restart_threshold, ipmi_status, test):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.threshold = int(threshold) # error threshold
        self.restart_threshold = int(restart_threshold) # not used
        self.interval = float(interval) # actual polling interval
        self.default_interval = self.interval # initial interval
        self.clusterId = clusterId
        self.test = test # unit test
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
            #check network status
            if self.checkNetworkStatus(self.node):
                #print "net ok"
                self.state_list[0] = 0
                #network ok
            else:
                #network error
                self.state_list[0] = self.state_list[0] + 1
                print "[" + self.node + "] 's network is unreachable"
                logging.error("DetectionManager PollingThread - The %s's network is unreachable.")

            #check service status
            try:
                line = "polling request"
                self.sock.sendall(line)
                data, addr = self.sock.recvfrom(1024)
                if data == "OK":
                    # service status 0 = ok
                    self.state_list[1] = 0
                    #print "["+self.node+"] OK" 
                        
                elif "error" in data :
		    print data
                    self.service_failure_data = data
                    self.state_list[1] = self.state_list[1] + 1
                    print "["+self.node+"]service Failed"
                elif not data:
                    self.state_list[1] = self.state_list[1] + 1
                    print "["+self.node+"]no ACK"
                else:
                    self.state_list[1] = self.state_list[1] + 1
                    print "["+self.node+"]Receive:"+data
                        
            except Exception as e:
                print "["+self.node+"] connection failed"
                self.sock.connect((self.node, self.port))
                self.service_failure_data = "agents"
                self.state_list[1] = self.state_list[1] + 1
            
            #check power status
            if self.ipmi_status:
                power_status = ipmi_manager.checkPowerStatus(self.node)
                if power_status == "OK":
                    #power ok
                    self.state_list[2] = 0
                    #print "power ok"
                elif power_status == "Error":
                    print "[" + self.node + "] 's power status is off"
                    self.state_list[2] = self.state_list[2] + 1
                    logging.error("DetectionManager PollingThread - The %s's power status is off." % self.node)
                    #power off
                else:
                    #logging.error("DetectionManager PollingThread - The %s's IPMI session can not be established.(power status)" % self.node)
                    self.ipmi_status = False

            #check os status
            if self.ipmi_status:
                os_status = ipmi_manager.checkOSstatus(self.node)
                if os_status == "OK":
                    #os ok
                    self.state_list[3] = 0
                    #print "os ok"
                elif os_status == "Error":
                    print "[" + self.node + "] 's watchdog timer cannot be reset"
                    self.state_list[3] = self.state_list[3] + 1
                    logging.error("DetectionManager PollingThread - The %s's watchdog timer cannot be reset." % self.node)

                    #reset watchdog with a little time
                    ipmi_manager.resetWatchDog(self.node)
                    #os failed
                else:
                    self.ipmi_status = False 

            #check sensor status
            if self.ipmi_status:
                sensor_status, critical_temp_sensor, critical_volt_sensor = ipmi_manager.checkSensorStatus(self.node)
                if sensor_status == "OK":
                    self.state_list[4] = 0
                    #print "sensor ok"
                elif sensor_status == "Error":
                    print "[ %s ] 's sensors value exceed threshold" % self.node
                    self.state_list[4] = self.state_list[4] + 1
                    if critical_temp_sensor:
                        self.print_critical_sensor(critical_temp_sensor, "temperature")
                    if critical_volt_sensor:
                        self.print_critical_sensor(critical_volt_sensor, "voltage")
                    logging.error("DetectionManager PollingThread - The %s's sensors value exceed threshold." % self.node)
                    #sensor failed
                else:
                    #logging.error("DetectionManager PollingThread - The %s's IPMI session can not be established.(sensor)" % self.node)
                    self.ipmi_status = False
            
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
                        slef.exit = True
                else:
                    logging.error("DetectionManager PollingThread - The %s has unknown failure so removed from cluster" % self.node)

                    server.recoveryVM(self.clusterId, self.node)
                    server.removeNodeFromCluster(self.clusterId, self.node)
                    self.exit = True
            else:
                time.sleep(self.interval)
                
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

    def checkNetworkStatus(self, node):
        status = True
        try:
            response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', node], stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError:
            status = False
        return status


def main():
    test = DetectionManager()
    while True:
        ch = raw_input("=>")
        if ch == "s":
            test.pollingRegister("test", "compute1")
        elif ch == "k":
            test.pollingCancel("test", "compute1")
    
if __name__ == "__main__":
    main()
