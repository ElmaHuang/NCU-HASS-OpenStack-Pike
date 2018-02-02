import socket
import sys
import time

import paramiko

sys.path.insert(0, '..')
from HASS.IPMIModule import IPMIManager
from HASS.Node import Node

CLUSTER_ID = "clusterid"
HOST = "compute2"
PORT = 2468

ipmi_manager = IPMIManager()


def run():
    client = _create_ssh_client(HOST)
    _remote_exec(client, "sudo systemctl stop networking.service")
    result = detection_network_fail(20)
    if result:
        print "detect network isolation successfully"
        recover = reboot_node(180)
        if recover:
            print "reboot node successfully"
        else:
            print "reboot node fail"
    else:
        print "detect network isolation fail"
    return result


def reboot_node(detect_time=5):
    ipmi_manager.rebootNode(HOST)
    result = False
    try:
        while detect_time > 0:
            state = _get_detect_result()
            if "health" in state:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Detect_Network recover-network-Except:" + str(e)
        result = False
    return result


def detection_network_fail(detect_time=5):
    result = False
    try:
        while detect_time > 0:
            fail = _get_detect_result()
            print fail
            if "network" in fail:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Detect_Network detect-network-Except:" + str(e)
        result = False
    return result


def _get_detect_result():
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    result = thread.detect()
    return result


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(name, username='root', timeout=default_timeout)
        return client
    except Exception as e:
        print "UT_Detect_Network create-ssh-Except: %s" % str(e)
        return None


def _check_boot_up():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    sock.settimeout(0.5)
    sock.connect((HOST, PORT))
    try:
        line = "polling request"
        sock.sendall(line)
        data, addr = sock.recvfrom(1024)
        return data
    except Exception as e:
        print "UT_Detect_Network check-boot-Except:" + str(e)
        return "Error"
