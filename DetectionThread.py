import sys
import threading
import time
import logging
import ConfigParser
import argparse
import xmlrpclib
import json
from Detector import Detector
import State


class DetectionThread(threading.Thread):
    def __init__(self, interval, threshold, clusterId, node, port, restart_threshold, ipmi_status):
        threading.Thread.__init__(self)
        self.threshold = int(threshold) # error threshold
        self.restart_threshold = int(restart_threshold) # not used
        self.interval = float(interval) # actual polling interval
        self.default_interval = self.interval # initial interval
        self.clusterId = clusterId
        self.node = node
        self.exit = False
        self.recovery_flag = True
        self.service_failure_data = ""
        self.ipmi_status = ipmi_status
        self.config = ConfigParser.RawConfigParser()
        self.config.read('failureTable.conf')
        self.detector = Detector(node, port)
        self.function_map = [self.detector.checkNetworkStatus, self.detector.checkOSStatus, self.detector.checkNetworkStatus, self.detector.checkServiceStatus]

    def run(self):
        data = ""
        failure_occured_time = 0
        failure_detection_time = 0
        
        while not self.exit:
            time.sleep(1)
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
            state = self.verify(_)
            if state == State.HEALTH:
                continue
            else:
                return state
        return State.HEALTH

    def verify(self, func):
        index = self.function_map.index(func)
        cloned_function_map = self.function_map[:] # clone from function map
        cloned_function_map = cloned_function_map[0:index+1] # remove uneeded detection function
        reversed_function_map = self._reverse(cloned_function_map)

        fail = None
        for _ in reversed_function_map:
            state = _()
            if state == State.HEALTH and _ == func:
                return State.HEALTH
            elif state == State.HEALTH:
                return fail
            elif not state == State.HEALTH:
                fail = state
        return fail

    def _reverse(self, list):
        list.reverse()
        return list