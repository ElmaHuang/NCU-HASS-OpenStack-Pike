#!/usr/bin/env python
# -*- coding: utf-8 -*-
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
import ConfigParser
import Config
import time

config = ConfigParser.RawConfigParser()
config.read('hass.conf')
auth = v3.Password(auth_url='http://controller:5000/v3',
                   username=config.get("openstack", "openstack_admin_account"),
                   password=config.get("openstack", "openstack_admin_password"),
                   project_name=config.get("openstack", "openstack_admin_account"),
                   user_domain_name=config.get("openstack", "openstack_user_domain_id"),
                   project_domain_name=config.get("openstack", "openstack_project_domain_id"))
sess = session.Session(auth=auth)
novaClient = client.Client(2.25, session=sess)


def create_provider_instance():
    if not _getInstanceByName(Config.INSTANCE_NAME):
        novaClient.servers.create(name=Config.INSTANCE_NAME,
                                  image=Config.IMAGE_ID,
                                  flavor=Config.FLAVOR_ID,
                                  availability_zone=Config.AVAILABILITY_ZONE,
                                  block_device_mapping=Config.BLOCK_DEVICE_MAPPING,
                                  nics=[{'net-id': Config.NETWORK_PROVIDER_ID}]
                                  )
    else:
        print "Preprocess : instance %s already exists!" % Config.INSTANCE_NAME
    if _InstanceActive(Config.INSTANCE_NAME):
        print "Preprocess : create instance %s success!" % Config.INSTANCE_NAME
    return _getInstanceIDByName(Config.INSTANCE_NAME)


def create_selfservice_instance():
    if not _getInstanceByName(Config.INSTANCE_NAME):
        novaClient.servers.create(name=Config.INSTANCE_NAME,
                                  image=Config.IMAGE_ID,
                                  flavor=Config.FLAVOR_ID,
                                  block_device_mapping=Config.BLOCK_DEVICE_MAPPING,
                                  nics=[{'net-id': Config.NETWORK_SELFSERVICE_ID}]
                                  )
    else:
        print "Preprocess : instance %s already exists!" % Config.INSTANCE_NAME
    if _InstanceActive(Config.INSTANCE_NAME):
        print "Preprocess : create instance %s success!" % Config.INSTANCE_NAME
    return _getInstanceIDByName(Config.INSTANCE_NAME)


def delete():
    instance = _getInstanceByName(Config.INSTANCE_NAME)
    novaClient.servers.force_delete(instance)

    time.sleep(5)
    if _getInstanceByName(Config.INSTANCE_NAME) == None:
        print "Postprocess : delete instance %s success!" % Config.INSTANCE_NAME
    return


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
    print "Instance not active"
    return False


if __name__ == '__main__':
    # create_provider_instance()
    # delete()
    pass
