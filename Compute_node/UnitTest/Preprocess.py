#!/usr/bin/env python
# -*- coding: utf-8 -*-


import UnitTestInstance


#
# III_SERVER_SUCCESS_MSG = "start/running"
# # III_SERVER_FAIL_MSG = "stop/waiting"
# III_SERVER_START_COMMAND = "service HASSd start"
# III_SERVER_STATUS_COMMAND = "service HASSd status"
# MOST_HASS_PATH = "/home/controller/Desktop/HASS/Controller_node/HASS/"
# MOST_SERVER_START_COMMAND = "python Hass.py &"


def do():
    pass


def create_instance():
    return UnitTestInstance.create_Instance_in_local_host()


def _get_instance_status():
    return UnitTestInstance._get_Instance_state_by_name()


def _get_instance_ip():
    return UnitTestInstance._get_Instance_ip()


def create_ssh_client(ip):
    return UnitTestInstance.create_ssh_client(ip)


def _remote_exec(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
    return stdin, stdout, stderr


def _deleteInstance():
    return UnitTestInstance.delete()


def test():
    print "test"


if __name__ == '__main__':
    pass
    # _createInstance()
    # _deleteInstance()
