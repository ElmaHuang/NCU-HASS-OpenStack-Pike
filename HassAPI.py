import xmlrpclib
import ConfigParser
import argparse

from prettytable import PrettyTable

class HassAPI():

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('hass.conf')
        self.authUrl = "http://"+self.config.get("rpc", "rpc_username")+":"+self.config.get("rpc", "rpc_password")+"@127.0.0.1:"+self.config.get("rpc", "rpc_bind_port")
        self.server = xmlrpclib.ServerProxy(self.authUrl)

        # global variable for sensor get mapping
        self.sensor_mapping = {"Temp": self.generateTempTable, "Voltage": self.generateVoltageTable}

    def generateTempTable(self,result):
        self.result_Temp_Table = PrettyTable(["Sensor ID", "Device", "Value", "Lower Critical", "Upper Critical"])
        for Temp_sensor_value in result:
            self.result_Temp_Table.add_row(Temp_sensor_value)
        return self.result_Temp_Table

    def generateVoltageTable(self,result):
        self.result_Voltage_Table = PrettyTable(["Sensor ID", "Device", "Value"])
        for Voltage_sensor_value  in result:
            self.result_Voltage_Table.add_row(Voltage_sensor_value)
        return self.result_Voltage_Table

    def bcolors(self):
        self.OK_color = '\033[92m'
        self.ERROR_color = '\033[91m'
        self.END_color = '\033[0m'

    def showResult(self,result):
        if result[0] == '0':
            return self.bcolors.OK_color + "[Success] " + self.bcolors.END_color + result[1]
        else:
            return self.bcolors.ERROR_color + "[Error] " + self.bcolors.END_color + result[1]

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

        if self.args.command is "cluster-create":
            if self.args.nodes is not None:
                self.HASS_result = self.server.createCluster(self.args.name, self.args.nodes.strip().split(",")).split(";")
            else:
                self.HASS_result = self.server.createCluster(self.args.name, []).split(";")
            #return createCluster_result["code"]+";"+createCluster_result["message"]

        elif self.args.command is "cluster-delete":
            self.HASS_result = self.server.deleteCluster(self.args.uuid).split(";")
            #return result["code"] + ";" + result["message"]


        elif self.args.command is "cluster-list":
            self.HASS_result = self.server.listCluster()

            self.cluster_table = PrettyTable(['UUID', 'Name'])
            for (uuid, name) in self.HASS_result :
                self.cluster_table.add_row([uuid, name])
            print self.cluster_table

        elif self.args.command is "node-add":
            self.HASS_result= self.server.addNode(self.args.uuid, self.args.nodes.strip().split(",")).split(";")
            #print showResult(result)

        elif self.args.command is "node-delete":
            self.HASS_result = self.server.deleteNode(self.args.uuid, self.args.node).split(";")
            #print showResult(result)

        elif self.args.command is "node-list":
            self.HASS_result= self.server.listNode(self.args.uuid)
            #return result["code"]+";"+result["nodeList"]

            if self.HASS_result.split(";")[0] is '0':
                print "Cluster uuid : " + self.args.uuid
                self.node_table = PrettyTable(["Count", "Nodes of HA Cluster"])
                self.node_counter = 0
                for node in self.HASS_result.split(";")[1].split(","):
                    self.node_counter = self.node_counter + 1

                    if node is not None:
                        self.node_table.add_row([str(self.node_counter), node])
                print self.node_table
            else:
                print self.HASS_result

        elif self.args.command is "node-start":
            self.HASS_result = self.server.startNode(self.args.node).split(";")
            #print showResult(result)

        elif self.args.command is "node-shutOff":
            self.HASS_result = self.server.shutOffNode(self.args.node).split(";")
            #print showResult(result)

        elif self.args.command is "node-reboot":
            self.HASS_result = self.server.rebootNode(self.args.node).split(";")
            #print showResult(result)

        elif self.args.command is "node-info-show":
            self.HASS_result = self.server.getAllInfoOfNode(self.args.node)
            #return result["code"]+";"+result["info"]

            self.temp_list = []
            self.volt_list = []
            if self.HASS_result.split(";")[0] is '0':
                print 'Computing Node : ' + self.args.node
                for sensor_value in self.HASS_result.split(";")[1]:
                    if "Temp" in sensor_value[0]:
                        self.temp_list.append(sensor_value)
                    else:
                        self.volt_list.append(sensor_value)
                print "Sensor type : Temperature"
                print self.generateTempTable(self.temp_list)
                print "Sensor type : Voltage"
                print self.generateVoltageTable(self.volt_list)
            else:
                print self.HASS_result

        elif self.args.command is "node-info-get":
            self.type_list = self.args.types.strip().split(",")
            self.HASS_result = self.server.getNodeInfoByType(self.args.node, self.type_list)
            #return result["code"]+";"+result["info"]

            if self.HASS_result.split(";")[0] is '0':
                print "Computing Node : " + self.args.node
                for sensor_type, sensor_value_list in zip(self.type_list, self.HASS_result.split(";")[1]):
                    print "Sensor type : ", sensor_type
                    # get corresponding table by sensor
                    self.sensor_table = self.sensor_mapping[sensor_type](sensor_value_list)
                    print self.sensor_table
            else:
                print self.HASS_result

        elif self.args.command is "instance-add":
            self.HASS_result = self.server.addInstance(self.args.uuid, self.args.vmid).split(";")
            #return result["code"]+";"+result["message"]
            #print showResult(result)

        elif self.args.command is "instance-delete":
            self.HASS_result = self.server.deleteInstance(self.args.uuid, self.args.vmid).split(";")
            #return result["code"] + ";" + result["message"]
            #print showResult(result)

        elif self.args.command is "instance-list":
            self.HASS_result = self.server.listInstance(self.args.uuid)
            #return result["code"]+";"+result["instanceList"]

            if self.HASS_result.split(";")[0] is '0':
                print "Cluster uuid : " + self.args.uuid
                self.instance_table = PrettyTable(["Count", "Below Host", "Instance ID"])
                self.instance_counter = 0
                for vmInfo in self.HASS_result.split(";")[1].split(","):
                    #vmInfo:
                    #instance[0] = instanceID
                    #instance[1] = Node Name
                    self.instance_counter += 1

                    if vmInfo is not None:
                        self.vm = vmInfo.split(":")
                        #instance of cluster = instanceID : instance node
                        self.instance_table.add_row([str(self.instance_counter), self.vm[0], self.vm[1]])
                print self.instance_table
            else:
                print self.HASS_result

        print self.showResult(self.HASS_result)


def main():
    hassapi=HassAPI()
    hassapi.Input_Command()
    hassapi.Input_Command_function()

if __name__ == "__main__":
    main()
