import socket
import subprocess
import sys
import time

import paramiko

sys.path.insert(0, '..')
from HASS.Node import Node
from HASS.IPMIModule import IPMIManager
from HASS.RecoveryManager import RecoveryManager

CLUSTER_ID = "clusterid"
HOST = "compute2"
PORT = 2468

ipmi_manager = IPMIManager()
recover = RecoveryManager()
node = Node(HOST, CLUSTER_ID)


def run():
    # shutoff node
    client = _create_ssh_client(HOST)
    _remote_exec(client, "sudo poweroff -f")
    time.sleep(30)
    # result = ipmi_manager.shutOffNode(HOST)
    # if result.code == "succeed":
    # print "shutoff node successfully"
    # start node
    try:
        result = recover.recoverNodeByStart(node)
        if result:
            return True
        else:
            return False
    except Exception as e:
        print "UT_Recover_Node_By_Start Except:" + str(e)
        return False
    # else:
    # return False


def recover_network_fail(detect_time=5):
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
        print "UT_Recover_Network_Isolation recover-network-Except:" + str(e)
        result = False
    return result


def detection_network_fail(detect_time=5):
    result = False
    try:
        while detect_time > 0:
            fail = _get_detect_result()
            if not fail:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Recover_Network_Isolation detect-network-Except:" + str(e)
        result = False
    return result


def _get_detect_result():
    try:
        response = subprocess.check_output(['timeout', '2', 'ping', '-c', '1', HOST], stderr=subprocess.STDOUT,
                                           universal_newlines=True)
        return True
    except:
        return False


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
        print "UT_Recover_Network_Isolation create-ssh-Except: %s" % str(e)
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
        print str(e)
        return "Error"
