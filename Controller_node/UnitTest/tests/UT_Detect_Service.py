import sys
import time

import paramiko

sys.path.insert(0, '..')
from HASS.Node import Node

CLUSTER_ID = "clusterid"
HOST = "compute2"
PORT = 2468


def run():
    client = _create_ssh_client(HOST)
    _remote_exec(client, "sudo service qemu-kvm stop")
    result = detection_service_fail(20)
    if result:
        print "detect qemu-kvm failure successfully"
        recover = start_service(client, 20)
        if recover:
            print "start service successfully"
        else:
            print "start service fail"
    else:
        print "detect qemu-kvm service failure fail"
    return result


def start_service(client, detect_time=5):
    _remote_exec(client, "sudo service qemu-kvm start")
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
        print "UT_Detect_Service start-service-Except:" + str(e)
        result = False
    return result


def detection_service_fail(detect_time=5):
    result = False
    try:
        while detect_time > 0:
            fail = _get_detect_result()
            print fail
            if "service" in fail:
                result = True
                break
            else:
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Detect_Service detect-service-Except:" + str(e)
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
        print "UT_Detect_Service create-ssh-Except:%s" % str(e)
        return None
