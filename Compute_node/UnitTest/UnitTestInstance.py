import ConfigParser
import subprocess
import time

import paramiko
from keystoneauth1 import session
from keystoneauth1.identity import v3
from novaclient import client

import Config

config = ConfigParser.RawConfigParser()
config.read('hass_node.conf')
host = subprocess.check_output(['hostname']).strip()
auth = v3.Password(auth_url='http://controller:5000/v3',
                   username=config.get("openstack", "openstack_admin_account"),
                   password=config.get("openstack", "openstack_admin_password"),
                   project_name=config.get("openstack", "openstack_admin_account"),
                   user_domain_name=config.get("openstack", "openstack_user_domain_id"),
                   project_domain_name=config.get("openstack", "openstack_project_domain_id"))
sess = session.Session(auth=auth)
novaClient = client.Client(2.25, session=sess)


def create_Instance_in_local_host():
    # novaClient.servers.create(name= 'test',
    # image = '66e04c13-646c-4470-a4ba-26160a6e076d',
    # flavor='0',
    # nics=[{'net-id':'d2e8a76c-c2aa-4e60-82ef-9ea7e297c86c'}])
    if not _getInstanceByName(Config.INSTANCE_NAME):
        novaClient.servers.create(name=Config.INSTANCE_NAME,
                                  image=Config.IMAGE_ID,
                                  flavor=Config.FLAVOR_ID,
                                  availability_zone="nova:%s" % host,
                                  block_device_mapping=Config.BLOCK_DEVICE_MAPPING,
                                  nics=[{'net-id': Config.NETWORK_PROVIDER_ID}]
                                  )
    else:
        print "Preprocess : instance %s already exists!" % Config.INSTANCE_NAME
    if _InstanceActive(Config.INSTANCE_NAME):
        print "Preprocess : create instance %s success!" % Config.INSTANCE_NAME
    else:
        print "%s is not ACTIVE!!" % Config.INSTANCE_NAME
    return _getInstanceIDByName(Config.INSTANCE_NAME)


def _get_Instance_ip():
    instance = _getInstanceByName(Config.INSTANCE_NAME)
    network_dict = getattr(instance, "networks")
    return network_dict.get('provider')[0]


def _get_Instance_state_by_name():
    instance = _getInstanceByName(Config.INSTANCE_NAME)
    return getattr(instance, 'status')


def _getInstanceByName(name):
    instance_list = novaClient.servers.list()
    for instance in instance_list:
        if getattr(instance, "name") == name:
            return instance
    return None


def _getInstanceIDByName(name):
    instance = _getInstanceByName(name)
    return getattr(instance, 'id')


def _InstanceActive(instance_name, time_out=60):
    while time_out > 0:
        try:
            instance = _getInstanceByName(instance_name)
            if getattr(instance, "status") == "ACTIVE":
                return True
        except Exception as e:
            print "Exception %s" % str(e)
        finally:
            time.sleep(1)
            time_out -= 1
    return False


def create_ssh_client(ip):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=Config.INSTANCE_USER_NAME, password=Config.INSTANCE_PASSWORD, timeout=5)
        return client
    except Exception as e:
        print "Excpeption : %s" % str(e)
        return None


def delete():
    instance = _getInstanceByName(Config.INSTANCE_NAME)
    novaClient.servers.force_delete(instance)
    time.sleep(5)
    if _getInstanceByName(Config.INSTANCE_NAME) == None:
        print "Postprocess : delete instance %s success!" % Config.INSTANCE_NAME
    return
