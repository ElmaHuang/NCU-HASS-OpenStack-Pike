#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Instance
import subprocess
import os

SERVER_SUCCESS_MSG = "start/running"
SERVER_FAIL_MSG = "stop/waiting"


def deleteInstance():
    return Instance.delete()


def server_stop(iii_support=True):
    if iii_support:
        _local_exec("service HASSd stop")
        status = _local_exec("service HASSd status")
        if SERVER_SUCCESS_MSG in status:
            raise Exception("Server didn't stop !")
    else:
        _local_exec("sudo killall python")

    print "SERVER STOP"


def _local_exec(cmd):
    p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, shell=False, stdout=open(os.devnull, 'w'))
    return p.communicate()
