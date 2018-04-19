import os
import subprocess
import sys
import time

import Postprocess
import Preprocess
import paramiko

sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from ClusterManager import ClusterManager

# sys.path.insert(0, '/home/' + HOST + '/Desktop/MOST/HASS/compute_node')
# from InstanceFailures import InstanceFailures

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]
HOST = "compute1"


def run():
    try:
        Preprocess.server_start(False)
        cluster_id, instance_id = _create_cluster()
        instance_name = Preprocess._get_instance_name(instance_id)
        client = _create_ssh_client(HOST)
        _instance_failure(client, instance_name)
        detection = detect_instance_status(20)
        if detection:
            return True
        else:
            return False
    except Exception as e:
        print str(e)
        return False
    finally:
        delete_cluster(cluster_id)
        Postprocess.server_stop(False)


def _create_cluster():
    ClusterManager.init()
    instance_id = Preprocess.create_with_provider_instance()
    cluster_id = ClusterManager.createCluster(CLUSTER_NAME, write_DB=False)
    cluster_id = cluster_id.data.get("cluster_id")
    ClusterManager.addNode(cluster_id, NODE_NAME, write_DB=False)
    ClusterManager.addInstance(cluster_id, instance_id, write_DB=False, send_flag=True)
    time.sleep(20)
    return cluster_id, instance_id


def delete_cluster(cluster_id):
    ClusterManager.deleteNode(cluster_id, HOST, write_DB=False)
    Postprocess.deleteInstance()


def _local_exec(cmd):
    p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, shell=False, stdout=open(os.devnull, 'w'))
    return p.communicate()


def _local_get_output(cmd):
    result = subprocess.check_output(cmd, shell=True)
    # print str(result)
    return result


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
    return stdin, stdout, stderr


def _create_ssh_client(name, default_timeout=1):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    try:
        client.connect(hostname=name, username='root', timeout=default_timeout)
        return client
    except Exception as e:
        print "Excpeption : %s" % str(e)
        return None


def detect_instance_status(timeout=5):
    result = False
    try:
        while timeout > 0:
            status = Preprocess._get_instance_status()
            if "ACTIVE" in status:
                result = True
                break
            else:
                timeout -= 1
                time.sleep(1)
    except Exception as e:
        print str(e)
        result = False
    finally:
        return result


def _instance_failure(client, instance_name):
    # result = False
    cmd = "sudo ps aux | grep " + instance_name + " | awk '{ print $2 }'"
    # cmd = "sudo hostname"
    i, o, e = _remote_exec(client, cmd)
    output = str(o.read())
    output = output.split()[0]
    # print output
    pid = output
    print "pid:", pid
    kill_cmd = "sudo kill -9 %s" % pid
    _remote_exec(client, kill_cmd)
    time.sleep(20)
    # print o.read()
