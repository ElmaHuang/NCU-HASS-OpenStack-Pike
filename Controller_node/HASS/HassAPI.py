#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   Command Line Interface for users.
##########################################################


from __future__ import print_function

import ConfigParser
import argparse
import xmlrpclib

from enum import Enum
from prettytable import PrettyTable

from Response import Response


class Table(Enum):
    CLUSTER = 'cluster'
    NODE = 'node'
    INSTANCE = 'instance'


class HassAPI(object):

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.authUrl = "http://" + self.config.get("rpc", "rpc_username") + ":" + self.config.get("rpc",
                                                                                                  "rpc_password") + \
                       "@127.0.0.1:" + self.config.get(
            "rpc", "rpc_bind_port")
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        # self.TABLE = Table()
        self.OK_color = '\033[92m'
        self.ERROR_color = '\033[91m'
        self.END_color = '\033[0m'

    def generateSensorTable(self, result):
        """

        :param result: 
        """
        if not result:
            raise Exception("There is no information")
        sensor_table = PrettyTable(
            ["Sensor ID", "Entity ID", "Sensor Type", "Value", "status", "lower_critical", "lower", "upper",
             "upper_critical"])
        for value in result:
            sensor_table.add_row(value)
        print(sensor_table)

    def showResult(self, result):
        """

        :param result: 
        :return: 
        """
        result = Response(code = result["code"], message = result["message"], data = result["data"])
        if result.code == "succeed":
            return self.OK_color + "[Success] " + self.END_color + result.message
        else:
            return self.ERROR_color + "[Error] " + self.END_color + result.message

    def showTable(self, result, table_type):
        """

        :param result: 
        :param table_type: 
        """
        # cluster list info
        if table_type == Table.CLUSTER:
            cluster_table = PrettyTable(['UUID', 'Name'])
            for (uuid, name) in result:
                cluster_table.add_row([uuid, name])
            print(cluster_table)
        # node list info
        elif table_type == Table.NODE:
            node_table = PrettyTable(["name", "cluster_id", "ipmi_enabled"])
            for name, cluster_id, ipmi_status in result:
                node_table.add_row([name, cluster_id, ipmi_status])
            print(node_table)
        elif table_type == Table.INSTANCE:
            instance_table = PrettyTable(["id", "name", "host", "state", "network"])
            for uuid, name, host, state, network in result:
                instance_table.add_row([uuid, name, host, state, network])
            print(instance_table)

    def Input_Command(self):
        """

        """
        self.parser = argparse.ArgumentParser(description = 'Openstack high availability software service(HASS)')
        subparsers = self.parser.add_subparsers(help = 'functions of HASS', dest = 'command')

        parser_cluster_create = subparsers.add_parser('cluster-create', help = 'Create a HA cluster')
        parser_cluster_create.add_argument("-n", "--name", help = "HA cluster name", required = True)
        parser_cluster_create.add_argument("-c", "--nodes",
                                           help = "Computing nodes you want to add to cluster. Use ',' to separate "
                                                  "nodes name")

        parser_cluster_delete = subparsers.add_parser('cluster-delete', help = 'Delete a HA cluster')
        parser_cluster_delete.add_argument("-i", "--uuid", help = "Cluster uuid you want to delete",
                                           required = True)

        parser_cluster_list = subparsers.add_parser('cluster-list', help = 'List all HA cluster')

        parser_node_add = subparsers.add_parser('node-add', help = 'Add computing node to HA cluster')
        parser_node_add.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)
        parser_node_add.add_argument("-c", "--nodes",
                                     help = "Computing nodes you want to add to cluster. Use ',' to separate nodes "
                                            "name",
                                     required = True)

        parser_node_delete = subparsers.add_parser('node-delete',
                                                   help = 'Delete computing node from HA cluster')
        parser_node_delete.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)
        parser_node_delete.add_argument("-c", "--node", help = "A computing node you want to delete from cluster.",
                                        required = True)

        parser_node_list = subparsers.add_parser('node-list', help = 'List all computing nodes of Ha cluster')
        parser_node_list.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)

        parser_node_start = subparsers.add_parser('node-start', help = 'Power on the computing node')
        parser_node_start.add_argument("-c", "--node", help = "Computing nodes you want to power on.",
                                       required = True)

        parser_node_shutoff = subparsers.add_parser('node-shutOff', help = 'Shut off the computing node')
        parser_node_shutoff.add_argument("-c", "--node", help = "Computing nodes you want to Shut off.",
                                         required = True)

        parser_node_reboot = subparsers.add_parser('node-reboot', help = 'Reboot the computing node')
        parser_node_reboot.add_argument("-c", "--node", help = "Computing nodes you want to reboot.",
                                        required = True)

        parser_node_getallinfo = subparsers.add_parser('node-info-show',
                                                       help = 'Get all hardware information of the computing node')
        parser_node_getallinfo.add_argument("-c", "--node",
                                            help = "Computing nodes you want to get all hardware information.",
                                            required = True)

        parser_node_getInfo_by_type = subparsers.add_parser('node-info-get',
                                                            help = 'Get detail hardware information of the '
                                                                   'computing node')
        parser_node_getInfo_by_type.add_argument("-c", "--node",
                                                 help = "Computing nodes you want to get detail hardware "
                                                        "information.",
                                                 required = True)
        parser_node_getInfo_by_type.add_argument("-t", "--types",
                                                 help = "The type of sensors which you want to get. Use ',"
                                                        "' to separate sensors' types",
                                                 required = True)

        parser_instance_add = subparsers.add_parser('instance-add',
                                                    help = 'Protect instance and add instance into HA cluster')
        parser_instance_add.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)
        parser_instance_add.add_argument("-v", "--vmid", help = "The ID of the instance you wand to protect",
                                         required = True)

        parser_instance_delete = subparsers.add_parser('instance-delete', help = 'remove instance protection')
        parser_instance_delete.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)
        parser_instance_delete.add_argument("-v", "--vmid",
                                            help = "The ID of the instance you wand to remove protection",
                                            required = True)

        parser_instance_list = subparsers.add_parser('instance-list', help = 'List all instances of Ha cluster')
        parser_instance_list.add_argument("-i", "--uuid", help = "HA cluster uuid", required = True)

    def Input_Command_function(self):
        """

        """
        args = self.parser.parse_args()
        if args.command == "cluster-create":
            try:
                if args.nodes is not None:
                    hass_result = self.server.createCluster(args.name, args.nodes.strip().split(","))
                else:
                    hass_result = self.server.createCluster(args.name, [])
                    # return createCluster_result["code"]+";"+createCluster_result["message"]
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "cluster-delete":
            try:
                hass_result = self.server.deleteCluster(args.uuid)
                # return result["code"] + ";" + result["message"]
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "cluster-list":
            try:
                hass_result = self.server.listCluster()
                self.showTable(hass_result, Table.CLUSTER)
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-add":
            try:
                hass_result = self.server.addNode(args.uuid, args.nodes.strip().split(","))
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-delete":
            try:
                hass_result = self.server.deleteNode(args.uuid, args.node)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-list":
            try:
                hass_result = self.server.listNode(args.uuid)
                if hass_result["code"] == "succeed":
                    hass_result = Response(code = hass_result["code"], message = hass_result["message"],
                                           data = hass_result["data"])
                    self.showTable(hass_result.data.get("node_list"), Table.NODE)
                else:
                    print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))
                # return

        elif args.command == "node-start":
            try:
                hass_result = self.server.startNode(args.node)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-shutOff":
            try:
                hass_result = self.server.shutOffNode(args.node)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-reboot":
            try:
                hass_result = self.server.rebootNode(args.node)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-info-show":
            try:
                hass_result = self.server.getAllInfoOfNode(args.node)
                if hass_result["code"] == "succeed":
                    self.generateSensorTable(hass_result["data"]["info"])
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "node-info-get":
            self.type_list = args.types.strip().split(",")
            try:
                hass_result = self.server.getNodeInfoByType(args.node, self.type_list)
                print("Computing Node : " + args.node)
                self.generateSensorTable(hass_result["data"]["info"])
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "instance-add":
            try:
                hass_result = self.server.addInstance(args.uuid, args.vmid)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "instance-delete":
            try:
                hass_result = self.server.deleteInstance(args.uuid, args.vmid)
                print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))

        elif args.command == "instance-list":
            try:
                hass_result = self.server.listInstance(args.uuid)
                if hass_result["code"] == "succeed":
                    hass_result = Response(code = hass_result["code"], message = hass_result["message"],
                                           data = hass_result["data"])
                    self.showTable(hass_result.data.get("instance_list"), Table.INSTANCE)
                else:
                    print(self.showResult(hass_result))
            except Exception as e:
                print(self.ERROR_color + "[Error] " + self.END_color + str(e))


def main():
    hassapi = HassAPI()
    hassapi.Input_Command()
    hassapi.Input_Command_function()


if __name__ == "__main__":
    main()
