#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

import UnitTestInstance

SERVER_SUCCESS_MSG = "start/running"
SERVER_FAIL_MSG = "stop/waiting"
GET_HASS_PID = "ps xu | grep Hass | grep -v grep | awk '{ print $2 }'"


def deleteInstance():
    return UnitTestInstance.delete()


# def server_stop(iii_support=True):
#     if iii_support:
#         _local_exec("service HASSd stop")
#         status = _local_exec("service HASSd status")
#         if SERVER_SUCCESS_MSG in status:
#             raise Exception("Server didn't stop !")
#     else:
#         pid = _local_get_output(GET_HASS_PID)
#         # print "result:", str(result)
#         _local_exec("sudo kill %s" % pid)
#
#     print "SERVER STOP"


def _local_exec(cmd):
    p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, shell=False, stdout=open(os.devnull, 'w'))
    return p.communicate()


def _local_get_output(cmd):
    result = subprocess.check_output(cmd, shell=True)
    # print str(result)
    return result
