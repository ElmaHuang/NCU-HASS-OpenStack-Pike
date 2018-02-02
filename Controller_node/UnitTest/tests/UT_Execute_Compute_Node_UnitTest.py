import os
import subprocess
# import sys
import time

import paramiko

# sys.path.insert(0, '/home/controller/Desktop/MOST/HASS')
from Controller_node.HASS.ClusterManager import ClusterManager
import Postprocess, Preprocess

CLUSTER_NAME = "cluster01"
NODE_NAME = ["compute1"]
HOST = "compute1"


def run():
    try:
        Preprocess.server_start(False)
        cluster_id, instance_id = _create_cluster()
        client = _create_ssh_client(HOST)
        result = exc_testagent(client)
        if result:
            return True
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


def exc_testagent(client):
    try:
        cmd = "sudo cd /home/" + HOST + "/Desktop/MOST/HASS/Compute_node/ ; python TestAgent.py"
        i, o, e = _remote_exec(client, cmd)
        result = o.read()
        return result
    except Exception as e:
        print str(e)
