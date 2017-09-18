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

        if self.args.command == "cluster-create":
            if self.args.nodes != None:
                self.HASS_result = self.server.createCluster(self.args.name, self.args.nodes.strip().split(",")).split(";")
            else:
                result = self.server.createCluster(self.args.name, []).split(";")
            print showResult(self.HASS_result)

        elif self.args.command == "cluster-delete":
            result = self.server.deleteCluster(args.uuid).split(";")
            print showResult(result)

        elif args.command == "cluster-list":
            result = server.listCluster()
            table = PrettyTable(['UUID', 'Name'])
            for (uuid, name) in result:
                table.add_row([uuid, name])
            print table

        elif args.command == "node-add":
            result = server.addNode(args.uuid, args.nodes.strip().split(",")).split(";")
            print showResult(result)

        elif args.command == "node-delete":
            result = server.deleteNode(args.uuid, args.node).split(";")
            print showResult(result)

        elif args.command == "node-list":
            result = server.listNode(args.uuid)
            if result.split(";")[0] == '0':
                print "Cluster uuid : " + args.uuid
                table = PrettyTable(["Count", "Nodes of HA Cluster"])
                counter = 0
                for node in result.split(";")[1].split(","):
                    counter = counter + 1
                    if node != '':
                        table.add_row([str(counter), node])
                print table
            else:
                print result

        elif args.command == "node-start":
            result = server.startNode(args.node).split(";")
            print showResult(result)

        elif args.command == "node-shutOff":
            result = server.shutOffNode(args.node).split(";")
            print showResult(result)

        elif args.command == "node-reboot":
            result = server.rebootNode(args.node).split(";")
            print showResult(result)

        elif args.command == "node-info-show":
            code, result = server.getAllInfoOfNode(args.node)
            temp_list = []
            volt_list = []
            if code == '0':
                print 'Computing Node : ' + args.node
                for sensor_value in result:
                    if "Temp" in sensor_value[0]:
                        temp_list.append(sensor_value)
                    else:
                        volt_list.append(sensor_value)
                print "Sensor type : Temperature"
                print generateTempTable(temp_list)
                print "Sensor type : Voltage"
                print generateVoltageTable(volt_list)
            else:
                print result

        elif args.command == "node-info-get":
            type_list = args.types.strip().split(",")
            code, result = server.getNodeInfoByType(args.node, type_list)
            if code == '0':
                print "Computing Node : " + args.node
                for sensor_type, sensor_value_list in zip(type_list, result):
                    print "Sensor type : ", sensor_type
                    # get corresponding table by sensor
                    table = sensor_mapping[sensor_type](sensor_value_list)
                    print table
            else:
                print result

        elif args.command == "instance-add":
            result = server.addInstance(args.uuid, args.vmid).split(";")
            print showResult(result)

        elif args.command == "instance-delete":
            result = server.deleteInstance(args.uuid, args.vmid).split(";")
            print showResult(result)

        elif args.command == "instance-list":
            result = server.listInstance(args.uuid)
            if result.split(";")[0] == '0':
                print "Cluster uuid : " + args.uuid
                table = PrettyTable(["Count", "Below Host", "Instance ID"])
                counter = 0
                for vmInfo in result.split(";")[1].split(","):
                    counter = counter + 1
                    if vmInfo != '':
                        vm = vmInfo.split(":")
                        table.add_row([str(counter), vm[0], vm[1]])
                print table
            else:
                print result




def main():


            

if __name__ == "__main__":
    main()
