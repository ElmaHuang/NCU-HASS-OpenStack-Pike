import sys
import time

import paramiko

sys.path.insert(0, '..')
from HASS.Node import Node
from HASS.NovaClient import NovaClient
import Postprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute2", "compute1"]
CLUSTER_ID = "clusterid"
HOST = "compute2"
TARGET_HOST = "compute1"
PORT = 2468
File_PATH = "/Desktop/HASS/Compute_node/UnitTest"
cmd = "sudo python stop_service.py &"


def run():
    try:
        client = _create_ssh_client(HOST)
        path = "cd /home/" + HOST + File_PATH + ";" + cmd
        _remote_exec(client, path)
        Recovery.recoverServiceFail(cluster_id, HOST)
        result = _checkEvacuate(instance_id, 180)
    except Exception as e:
        print "UT_Recover_Service_by_Evacuate Except:" + str(e)
        result = False
    finally:
        Postprocess.deleteInstance()
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
        print "UT_Recover_Qemu-KVM_Service detect-qemu-Except:" + str(e)
        result = False
    return result


def _get_detect_result():
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    result = thread.detect()
    return result


def _checkEvacuate(instance_id, detect_time=20):
    novaClient = NovaClient.getInstance()
    try:
        while detect_time > 0:
            if novaClient.getInstanceHost(instance_id) == TARGET_HOST:
                result = True
                break
            else:
                result = False
                detect_time -= 1
                time.sleep(1)
    except Exception as e:
        print "UT_Recover_Service_by_Evacuate  check evacuate-Except:" + str(e)
        result = False
    finally:
        return result


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    print stdout.read()
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(name, username='root', timeout=default_timeout)
        return client
    except Exception as e:
        print "UT_Recover_Service create-ssh-Except:%s" % str(e)
        return None
