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
    try:
        client = _create_ssh_client(HOST)
        _remote_exec(client, "sudo poweroff -f")
        print "wait %s to shutoff" % HOST
        time.sleep(15)
        result = detection_power_fail(20)
        if result:
            print "detect power status successfully"
            recover = power_on(180)
            if recover:
                print "boot node successfully"
            else:
                print "boot node fail"
        else:
            print "detect power status fail"
        return result
    except Exception as e:
        print "UT_Detect_Power Except:" + str(e)


def power_on(detect_time=5):
    ipmi_manager.startNode(HOST)
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
        print "UT_Detect_Power recover-power-Except:" + str(e)
        result = False
    return result


def detection_power_fail(detect_time=5):
    result = False
    try:
        while detect_time > 0:
            fail = _get_detect_result()
            print fail
            if "power" in fail:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Detect_Power detect-power-Except:" + str(e)
        result = False
    return result


def _get_detect_result():
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    result = thread.detect()
    return result


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(name, username='root', timeout=default_timeout)
        return client
    except Exception as e:
        print "UT_Recover_Power_Status create-ssh-Except: %s" % str(e)
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
        print "UT_Recover_Power_Status check-boot-Except:" + str(e)
        return "Error"
