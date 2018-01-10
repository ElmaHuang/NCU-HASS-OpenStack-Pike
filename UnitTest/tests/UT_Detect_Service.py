import sys

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from DetectionThread import DetectionThread
from Node import Node
import Preprocess
import Postprocess
import Config
import paramiko
import time

CLUSTER_ID = "clusterid"
HOST = "compute3"
PORT = 2468


def run():
    node = Node(HOST, CLUSTER_ID)
    thread = node.detection_thread
    client = _create_ssh_client(HOST)
    _remote_exec(client, "sudo service qemu-kvm stop")
    try:
        detect_time = 5
        while detect_time > 0:
            fail = thread.detect()
            print fail
            if fail == "service":
                return True
            detect_time -= 1
            time.sleep(1)
        return False
    except Exception as e:
        print str(e)
    finally:
        _remote_exec(client, "sudo service qemu-kvm start")


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
        print "Excpeption : %s" % str(e)
        return None
