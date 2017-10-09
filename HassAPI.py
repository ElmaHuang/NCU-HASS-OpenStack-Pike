import xmlrpclib
import ConfigParser
import argparse

from enum import Enum
from prettytable import PrettyTable

def enum(**enums):
    return type('Enum', (), enums)

class HassAPI():

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.authUrl = "http://"+self.config.get("rpc", "rpc_username")+":"+self.config.get("rpc", "rpc_password")+"@127.0.0.1:"+self.config.get("rpc", "rpc_bind_port")
        self.server = xmlrpclib.ServerProxy(self.authUrl)
        self.HASS_result = None
        # global variable for sensor get mapping
        self.TABLE = enum(CLUSTER='cluster', NODE='node', INSTANCE='instance')
        self.bcolors()

    # def generateTempTable(self,result):
    #     self.result_Temp_Table = PrettyTable(["Sensor ID", "Device", "Value", "Lower Critical", "Upper Critical"])
    #     self.result_Temp_Table.add_row(result)
    #     return self.result_Temp_Table

    # def generateVoltageTable(self,result):
    #     self.result_Voltage_Table = PrettyTable(["Sensor ID", "Device", "Value"])
    #     for Voltage_sensor_value  in result:
    #         self.result_Voltage_Table.add_row(Voltage_sensor_value)
    #     return self.result_Voltage_Table

    def generateSensorTable(self, result):
        sensor_table = PrettyTable(["Sensor ID", "Entity ID", "Sensor Type", "Value", "status"])
        for value in result:
            sensor_table.add_row(value)
        print sensor_table

    def bcolors(self):
        self.OK_color = '\033[92m'
        self.ERROR_color = '\033[91m'
        self.END_color = '\033[0m'

    def showResult(self,result):
        if result[0] == '0':
            return self.OK_color + "[Success] " + self.END_color + result[1]
        else:
            return self.ERROR_color + "[Error] " + self.END_color + result[1]

    def showTable(self, result , type):
        # cluster list info
        if type == self.TABLE.CLUSTER:
            self.cluster_table = PrettyTable(['UUID', 'Name'])
            for (uuid, name) in self.HASS_result :
                self.cluster_table.add_row([uuid, name])
            print self.cluster_table
        # node list info
        elif type == self.TABLE.NODE:
            self.node_table = PrettyTable(["id", "name","cluster_id"])
            for name,cluster_id in self.HASS_result:
                self.node_table.add_row([name,cluster_id])
            print self.node_table
        elif type == self.TABLE.INSTANCE:
            self.instance_table = PrettyTable(["id", "name","host"])
            for id,name,host in self.HASS_result:
                self.instance_table.add_row([id,name,host])
            print self.instance_table

    def Input_Command(self):

        self.parser = argparse.ArgumentParser(description='Openstack high availability software service(HASS)')
        self.subparsers = self.parser.add_subparsers(help='functions of HASS', dest='command')

        self.parser_cluster_create = self.subparsers.add_parser('cluster-create', help='Create a HA cluster')
        self.parser_cluster_create.add_argument("-n", "--name", help="HA cluster name", required=True)
        self.parser_cluster_create.add_argument("-c", "--nodes",help="Computing nodes you want to add to cluster. Use ',' to separate nodes name")

        self.parser_cluster_delete = self.subparsers.add_parser('cluster-delete', help='Delete a HA cluster')
        self.parser_cluster_delete.add_argument("-i", "--uuid", help="Cluster uuid you want to delete", required=True)

        self.parser_cluster_list = self.subparsers.add_parser('cluster-list', help='List all HA cluster')

        self.parser_node_add = self.subparsers.add_parser('node-add', help='Add computing node to HA cluster')
        self.parser_node_add.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)
        self.parser_node_add.add_argument("-c", "--nodes",help="Computing nodes you want to add to cluster. Use ',' to separate nodes name",required=True)

        self.parser_node_delete = self.subparsers.add_parser('node-delete', help='Delete computing node from HA cluster')
        self.parser_node_delete.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)
        self.parser_node_delete.add_argument("-c", "--node", help="A computing node you want to delete from cluster.",required=True)

        self.parser_node_list = self.subparsers.add_parser('node-list', help='List all computing nodes of Ha cluster')
        self.parser_node_list.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)

        self.parser_node_start = self.subparsers.add_parser('node-start', help='Power on the computing node')
        self.parser_node_start.add_argument("-c", "--node", help="Computing nodes you want to power on.", required=True)

        self.parser_node_shutOff = self.subparsers.add_parser('node-shutOff', help='Shut off the computing node')
        self.parser_node_shutOff.add_argument("-c", "--node", help="Computing nodes you want to Shut off.", required=True)

        self.parser_node_reboot = self.subparsers.add_parser('node-reboot', help='Reboot the computing node')
        self.parser_node_reboot.add_argument("-c", "--node", help="Computing nodes you want to reboot.", required=True)

        self.parser_node_getAllInfo = self.subparsers.add_parser('node-info-show',help='Get all hardware information of the computing node')
        self.parser_node_getAllInfo.add_argument("-c", "--node",help="Computing nodes you want to get all hardware information.",required=True)

        self.parser_node_getInfo_by_type = self.subparsers.add_parser('node-info-get',help='Get detail hardware information of the computing node')
        self.parser_node_getInfo_by_type.add_argument("-c", "--node",help="Computing nodes you want to get detail hardware information.",required=True)
        self.parser_node_getInfo_by_type.add_argument("-t", "--types",help="The type of sensors which you want to get. Use ',' to separate sensors' types",required=True)

        self.parser_instance_add = self.subparsers.add_parser('instance-add',help='Protect instance and add instance into HA cluster')
        self.parser_instance_add.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)
        self.parser_instance_add.add_argument("-v", "--vmid", help="The ID of the instance you wand to protect",required=True)

        self.parser_instance_delete = self.subparsers.add_parser('instance-delete', help='remove instance protection')
        self.parser_instance_delete.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)
        self.parser_instance_delete.add_argument("-v", "--vmid", help="The ID of the instance you wand to remove protection",required=True)

        self.parser_instance_list = self.subparsers.add_parser('instance-list', help='List all instances of Ha cluster')
        self.parser_instance_list.add_argument("-i", "--uuid", help="HA cluster uuid", required=True)

    def Input_Command_function(self):
        self.args = self.parser.parse_args()
        if self.args.command == "cluster-create":
            if self.args.nodes != None:
                self.HASS_result = self.server.createCluster(self.args.name, self.args.nodes.strip().split(",")).split(";")
            else:
                self.HASS_result = self.server.createCluster(self.args.name, []).split(";")
            #return createCluster_result["code"]+";"+createCluster_result["message"]
            print self.showResult(self.HASS_result)

        elif self.args.command == "cluster-delete":
            self.HASS_result = self.server.deleteCluster(self.args.uuid).split(";")
            #return result["code"] + ";" + result["message"]
            print self.showResult(self.HASS_result)

        elif self.args.command == "cluster-list":
            self.HASS_result = self.server.listCluster()
            self.showTable(self.HASS_result , self.TABLE.CLUSTER)

        elif self.args.command == "node-add":
            self.HASS_result= self.server.addNode(self.args.uuid, self.args.nodes.strip().split(",")).split(";")
            print self.showResult(self.HASS_result)

        elif self.args.command == "node-delete":
            self.HASS_result = self.server.deleteNode(self.args.uuid, self.args.node).split(";")
            print self.showResult(self.HASS_result)

        elif self.args.command == "node-list":
            try:
                self.HASS_result= self.server.listNode(self.args.uuid)
            except Exception as e:
               print self.ERROR_color + "[Error] " + self.END_color + str(e)
               return
            self.showTable(self.HASS_result, self.TABLE.NODE)

        elif self.args.command == "node-start":
            try:
                self.HASS_result = self.server.startNode(self.args.node).split(";")
                print self.showResult(self.HASS_result)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)

        elif self.args.command == "node-shutOff":
            try:
                self.HASS_result = self.server.shutOffNode(self.args.node).split(";")
                print self.showResult(self.HASS_result)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)

        elif self.args.command == "node-reboot":
            try:
                self.HASS_result = self.server.rebootNode(self.args.node).split(";")
                print self.showResult(self.HASS_result)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)

        elif self.args.command == "node-info-show":
            try:
                code , result = self.server.getAllInfoOfNode(self.args.node)
                print self.generateSensorTable(result)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)

        elif self.args.command == "node-info-get":
            self.type_list = self.args.types.strip().split(",")
            try:
                code, self.HASS_result = self.server.getNodeInfoByType(self.args.node, self.type_list)
                print "Computing Node : " + self.args.node
                self.generateSensorTable(self.HASS_result)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e) 

        elif self.args.command == "instance-add":
            try:
                self.HASS_result = self.server.addInstance(self.args.uuid, self.args.vmid).split(";")
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)
                return

            print self.showResult(self.HASS_result)

        elif self.args.command == "instance-delete":
            self.HASS_result = self.server.deleteInstance(self.args.uuid, self.args.vmid).split(";")
            #return result["code"] + ";" + result["message"]
            print self.showResult(self.HASS_result)

        elif self.args.command == "instance-list":
            try:
                self.HASS_result = self.server.listInstance(self.args.uuid)
            except Exception as e:
                print self.ERROR_color + "[Error] " + self.END_color + str(e)
                return
            #return result["code"]+";"+result["instanceList"]
            self.showTable(self.HASS_result, self.TABLE.INSTANCE)


def main():
    hassapi=HassAPI()
    hassapi.Input_Command()
    hassapi.Input_Command_function()

if __name__ == "__main__":
    main()
