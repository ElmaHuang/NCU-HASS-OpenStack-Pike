#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains recovery methods.
##########################################################


from __future__ import print_function

import ConfigParser
import logging
import subprocess
import time

import State
from ClusterManager import ClusterManager
from DatabaseManager import IIIDatabaseManager
from Detector import Detector
from NovaClient import NovaClient


class RecoveryManager(object):
    def __init__(self):
        self.nova_client = NovaClient.getInstance()
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.recover_function = {
            State.NETWORK_FAIL: self.recoverNetworkIsolation,
            State.SERVICE_FAIL: self.recoverServiceFail,
            State.POWER_FAIL: self.recoverPowerOff,
            State.SENSOR_FAIL: self.recoverSensorCritical,
            State.SENSOR_CONFIG_FAIL: self.recoverSensorCriticalByConfig,
            State.OS_FAIL: self.recoverOSHanged
            }
        self.iii_support = self.config.getboolean("iii", "iii_support")
        self.iii_database = None

    def recover(self, fail_type, cluster_id, fail_node_name):
        """

        :param fail_type: 
        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        return self.recover_function[fail_type](cluster_id, fail_node_name)

    def recoverOSHanged(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        start_os_recover_vm = time.time()
        print("start recover vm :%s" % str(start_os_recover_vm))
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print("fail node is %s" % fail_node.name)
        print("start recovery vm")
        self.recoverVMByEvacuate(cluster, fail_node)
        finish_os_recover_vm = time.time()
        print("vm recovery time : %s" % str(finish_os_recover_vm - start_os_recover_vm))
        print("end recovery vm")
        # return self.recoverNodeByReboot(fail_node)
        temp = self.recoverNodeByReboot(fail_node)
        start_os_recover_host = time.time()
        print("host recovery time : %s" % str(start_os_recover_host - finish_os_recover_vm))
        return temp

    def recoverPowerOff(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        print("start recover power off")
        start_power_recover_vm = time.time()
        print("%s" % str(start_power_recover_vm))
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print("fail node is %s" % fail_node.name)
        print("start recovery vm")
        self.recoverVMByEvacuate(cluster, fail_node)
        finish_power_recover_vm = time.time()
        print("vm recovery time : %s" % str(finish_power_recover_vm - start_power_recover_vm))
        print("end recovery vm")
        # return self.recoverNodeByStart(fail_node)
        temp = self.recoverNodeByStart(fail_node)
        finish_power_recover_host = time.time()
        print("host recovery time : %s" % str(finish_power_recover_host - finish_power_recover_vm))
        return temp

    def recoverNetworkIsolation(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        start_net_recover_vm = time.time()
        print("start recover vm :%s" % str(start_net_recover_vm))
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)

        network_transient_time = int(self.config.get("default", "network_transient_time"))
        second_chance = State.HEALTH
        try:
            print("start second_chance...")
            print("wait %s seconds and check again" % network_transient_time)
            time.sleep(network_transient_time)  # sleep certain transient seconds and ping host again
            response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', fail_node.name],
                                               stderr = subprocess.STDOUT, universal_newlines = True)
        except subprocess.CalledProcessError:
            print("After 30 senconds, the network status of %s is still unreachable" % fail_node.name)
            second_chance = State.NETWORK_FAIL

        if second_chance == State.HEALTH:
            print("The network status of %s return to health" % fail_node.name)
            return True
        else:
            print("fail node is %s" % fail_node.name)
            start_net_recover_vm = time.time()
            print("start recovery vm", start_net_recover_vm)
            self.recoverVMByEvacuate(cluster, fail_node)
            finish_net_recover_vm = time.time()
            print("vm recovery time : %s" % str(finish_net_recover_vm - start_net_recover_vm))
            print("end recovery vm")
            # return self.recoverNodeByReboot(fail_node)
            start_net_recover_host = time.time()
            temp = self.recoverNodeByReboot(fail_node)
            finish_net_recover_host = time.time()
            print("host recovery time : %s" % str(finish_net_recover_host - start_net_recover_host))
            return temp

    def recoverSensorCritical(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print("fail node is %s" % fail_node.name)
        print("start recovery vm")
        self.recoverVMByEvacuate(cluster, fail_node)
        # self.recoverVMByLiveMigrate(cluster, fail_node)
        print("end evacuate vm")
        return self.recoverNodeByShutoff(fail_node)

    def recoverSensorCriticalByConfig(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        print("start recover sensor:", time.time())
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print("start recover vm:", time.time())
        self.recoverVMByLiveMigrate(cluster, fail_node)
        # self.recoverVMByEvacuate(cluster, fail_node) # test
        print("end recover vm and start reboot host", time.time())
        # return self.recoverNodeByReboot(fail_node)
        temp = self.recoverNodeByReboot(fail_node)
        print("finish recover host:", time.time())
        return temp
        # return True

    def recoverServiceFail(self, cluster_id, fail_node_name):
        """

        :param cluster_id: 
        :param fail_node_name: 
        :return: 
        """
        finish_detect_service_vm = time.time()
        print("detect service fail", finish_detect_service_vm)
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        port = int(self.config.get("detection", "polling_port"))
        version = int(self.config.get("version", "version"))
        detector = Detector(fail_node, port)
        fail_services = detector.getFailServices()
        if fail_services is None:
            logging.info("get fail service equals to None, abort recover service fail")
            return True
        # status = True
        if "agents" in fail_services:
            status = self.restartDetectionService(fail_node, version)
        else:
            start_restart_service = time.time()
            print("start restart service:", start_restart_service)
            status = self.restartServices(fail_node, fail_services, version)
            # status = False
        if not status:  # restart service fail
            print("start recovery service fail")
            print("fail node is %s" % fail_node.name)
            start_recover_service_vm = time.time()
            print("start recovery vm", start_recover_service_vm)
            self.recoverVMByEvacuate(cluster, fail_node)
            finish_recover_service_vm = time.time()
            print("end recovery vm", finish_recover_service_vm)
            return self.recoverNodeByReboot(fail_node)
            # temp = self.recoverNodeByReboot(fail_node)
            # finish_recover_service_host = time.time()
            # print("end recovery host", finish_recover_service_host)
            # return temp
        else:  # restart service success
            finish_restart_service = time.time()
            print("finish restart service:", finish_restart_service)
            return status  # restart service success

    def recoverVMByLiveMigrate(self, cluster, fail_node):
        """

        :param cluster: 
        :param fail_node: 
        :return: 
        """
        if len(cluster.node_list) < 2:
            message = "RecoverManager : evacuate fail, cluster only one node"
            print(message)
            logging.error(message)
            return
        if not fail_node:
            message = "RecoverManager : not found the fail node"
            print(message)
            logging.error(message)
            return
        protected_instance_list = cluster.getProtectedInstanceListByNode(fail_node)
        for instance in protected_instance_list:
            try:
                print("start live migration")
                target_host = cluster.liveMigrateInstance(instance.id)
                if target_host == fail_node.name or target_host not in cluster.getAllNodeStr():
                    print("live migration fail")
                    logging.error(
                        "RecoveryManager recoverVMByLiveMigrate live migration fail .cluster_id = %s ,instance_id "
                        "=%s" % (
                            cluster.id, instance.id))
                else:
                    print("live migration success")
                    print("check instance network status")
                    status = self.checkInstanceNetworkStatus(fail_node, cluster)
                    if not status:
                        logging.error("RecoverManager : check vm network status false")
                    print("check vm net finish:", time.time())
            except Exception as e:
                print("RecoveryManager recoverVMByLiveMigrate --Except:" + str(e))
                logging.error("RecoverManager - The instance %s live migrate failed" % instance.id)
            finally:
                print("update instance")
                cluster.updateInstance()

    def recoverVMByEvacuate(self, cluster, fail_node):
        """

        :param cluster: 
        :param fail_node: 
        :return: 
        """
        # start_power_recover_vm = time.time()
        if len(cluster.node_list) < 2:
            message = "RecoverManager : evacuate fail, cluster only one node"
            print(message)
            logging.error(message)
            return
        if not fail_node:
            message = "RecoverManager : not found the fail node"
            print(message)
            logging.error(message)
            return
        target_host = cluster.findTargetHost(fail_node)
        print("target_host : %s" % target_host.name)
        if not target_host:
            logging.error("RecoverManager : not found the target_host %s" % target_host)
        protected_instance_list = cluster.getProtectedInstanceListByNode(fail_node)
        print("protected list : %s" % protected_instance_list)
        for instance in protected_instance_list:
            if target_host.instanceOverlappingInLibvirt(instance):
                print("instance %s overlapping in %s" % (instance.name, target_host.name))
                print("start undefine instance in %s" % target_host.name)
                target_host.undefineInstance(instance)
                print("end undefine instance")
            try:
                print("start evacuate")
                final_host = cluster.evacuate(instance, target_host, fail_node)
                if final_host == fail_node.name:
                    print("evacuate fail")
                    logging.error(
                        "RecoveryManager recoverVMByEvacuate evacuate fail .cluster_id = %s ,instance_id =%s" % (
                            cluster.id, instance.id))
                else:
                    print("evacuate success")
                    print("check instance network status")
                    status = self.checkInstanceNetworkStatus(fail_node, cluster)
                    print("network status:", status)
                    if not status:
                        logging.error("RecoverManager : check vm network status false")
                    ping_vm = time.time()
                    print("recover finish and ping vm success : ", ping_vm)
            except Exception as e:
                print("RecoveryManager recoverVMByEvacuate --Except:" + str(e))
                logging.error("RecoverManager - The instance %s evacuate failed" % instance.id)
            finally:
                print("update instance")
                cluster.updateInstance()

        if self.iii_support:
            self.iii_database = IIIDatabaseManager()
            print("start modify iii database")
            for instance in protected_instance_list:
                try:
                    self.iii_database.updateInstance(instance.id, target_host.name)
                except Exception as e:
                    message = "RecoveryManager recoverVM for iii --Except:" + str(e)
                    print(message)
                    logging.error(message)
            print("end modify iii database")

    def recoverNodeByReboot(self, fail_node):
        """

        :param fail_node: 
        :return: 
        """
        print("start recover node by reboot")
        result = fail_node.reboot()
        message = "RecoveryManager recover node by reboot finish"
        print("boot node result : %s" % result.message)
        if result.code == "succeed":
            logging.info(message + result.message)
            boot_up = self.checkNodeBootSuccess(fail_node)
            if boot_up:
                print("Node %s recovery finished." % fail_node.name)
                return True
            else:
                logging.error(message + "Can not reboot node %s successfully", fail_node.name)
                return False
        else:
            logging.error(message + result.message)
            return False

    def recoverNodeByShutoff(self, fail_node):
        """

        :param fail_node: 
        :return: 
        """
        print("start recover node by shutoff")
        result = fail_node.shutoff()
        if result.code == "succeed":
            return False  # shutoff need to remove from cluster, so return False
        else:
            logging.error(result.message)
            print(result.message)

    def recoverNodeByStart(self, fail_node):
        """

        :param fail_node: 
        :return: 
        """
        print("start recover node by start")
        result = fail_node.start()
        print("boot node result : %s" % result.message)
        message = "RecoveryManager recover node by start"
        if result.code == "succeed":
            logging.info(message + result.message)
            boot_up = self.checkNodeBootSuccess(fail_node)
            if boot_up:
                print("Node %s recovery finished." % fail_node.name)
                return True
            else:
                logging.error(message + "Can not start node %s successfully", fail_node.name)
                return False
        else:
            logging.error(message + result.message)
            return False

    def restartDetectionService(self, fail_node, version):
        """

        :param fail_node: 
        :param version: 
        :return: 
        """
        agent_path = self.config.get("path", "agent_path")
        find_detection_cmd = "ps aux | grep '[D]etectionAgent.py'"
        # start_detection_cmd = "cd /home/%s/%s/ ; python DetectionAgent.py" % (fail_node.name, agent_path)  # not
        # daemon
        start_detection_cmd = "systemctl restart detectionagent.service"
        try:
            # kill crash detection agent
            agent_pid = find_detection_cmd.split()[1]
            kill_detection_cmd = "kill -9 %s" % agent_pid
            fail_node.remote_exec(kill_detection_cmd)
            # start detection agent
            print("Start service failure recovery by starting Detection Agent")
            fail_node.remote_exec(start_detection_cmd)  # restart DetectionAgent service
            time.sleep(5)
            stdin, stdout, stderr = fail_node.remote_exec(find_detection_cmd)
            service = stdout.read()
            print(service)
            if "python DetectionAgent.py" in service:  # check DetectionAgent
                return True
            return False
        except Exception as e:
            print("RecoveryManager restartDetectionService --Except:" + str(e))
            return False

    def restartServices(self, fail_node, fail_services, version, check_timeout = 60):
        """

        :param fail_node: 
        :param fail_services: 
        :param version: 
        :param check_timeout: 
        :return: 
        """
        service_mapping = {"libvirt": "libvirt-bin", "nova": "nova-compute", "qemukvm": "qemu-kvm"}
        fail_service_list = fail_services.split(":")[-1].split(";")[0:-1]

        try:
            for fail_service in fail_service_list:
                fail_service = service_mapping[fail_service]
                if version == 16:
                    cmd = "systemctl restart %s" % fail_service
                else:
                    cmd = "sudo service %s restart" % fail_service
                stdin, stdout, stderr = fail_node.remote_exec(cmd)  # restart service
                time.sleep(1)

                while check_timeout > 0:
                    if version == 14:
                        cmd = "service %s status" % fail_service
                    elif version == 16:
                        cmd = "systemctl status %s | grep dead" % fail_service
                    stdin, stdout, stderr = fail_node.remote_exec(cmd)  # check service active or not
                    res = stdout.read()
                    # for version 14
                    if version == 14:
                        if not res:
                            print("The node %s service %s still doesn't work" % (fail_node.name, fail_service))
                        else:
                            print("The node %s service %s successfully restart" % (fail_node.name, fail_service))
                            return True  # recover all the fail service
                    else:
                        # for version 16
                        if res:
                            print("The node %s service %s still doesn't work" % (fail_node.name, fail_service))
                        else:
                            print("The node %s service %s successfully restart" % (fail_node.name, fail_service))
                            return True  # recover all the fail service

                    check_timeout -= 1
                return False
        except Exception as e:
            print("RecoveryManager restartServices --Except:" + str(e))
            return False

    def checkInstanceNetworkStatus(self, fail_node, cluster, check_timeout = 60):
        """

        :param fail_node: 
        :param cluster: 
        :param check_timeout: 
        :return: 
        """
        status = False
        protected_instance_list = cluster.getProtectedInstanceListByNode(fail_node)
        for instance in protected_instance_list:
            ip = instance.ext_net
            try:
                if ip is None:
                    print("vm : %s has no floating network, abort ping process!" % instance.name)
                    status = True
                else:
                    ip = str(ip)
                    status = self._pingInstance(ip, check_timeout)
            except Exception as e:
                print(str(e))
                # continue
            if not status:
                print("ping vm fail")
                logging.error("vm %s cannot ping %s" % (instance.name, ip))
            else:
                print("ping vm success")
        return status

    def _pingInstance(self, ip, check_timeout):
        status = False
        time.sleep(5)
        while check_timeout > 0:
            try:
                print("check vm %s" % ip)
                response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', ip],
                                                   stderr = subprocess.STDOUT,
                                                   universal_newlines = True)
                status = True
                break
            except subprocess.CalledProcessError:
                status = False
            finally:
                time.sleep(1)
                check_timeout -= 1
        return status

    def checkNodeBootSuccess(self, node, check_timeout = 300):
        """

        :param node: 
        :param check_timeout: 
        :return: 
        """
        port = int(self.config.get("detection", "polling_port"))
        detector = Detector(node, port)
        print("waiting node to boot up")
        time.sleep(5)
        print("start check node booting")
        while check_timeout > 0:
            try:
                if detector.checkServiceStatus() == State.HEALTH:
                    return True
            except Exception as e:
                print("RecoveryManager checkNodeBootSuccess --Except:" + str(e))
            finally:
                time.sleep(1)
                check_timeout -= 1
        return False


if __name__ == "__main__":
    r = RecoveryManager()
    # l = r.remote_exec("compute3","virsh list --all")
    '''
    def recoverNodeCrash(self, cluster_id, fail_node_name):
        cluster = ClusterManager.getCluster(cluster_id)
        if not cluster:
            logging.error("RecoverManager : cluster not found")
            return
        fail_node = cluster.getNodeByName(fail_node_name)
        print "fail node is %s" % fail_node.name
        print "start recovery vm"
        self.recoverVMByEvacuate(cluster, fail_node)
        print "end recovery vm"
        return self.recoverNodeByShutoff(fail_node)
    '''
