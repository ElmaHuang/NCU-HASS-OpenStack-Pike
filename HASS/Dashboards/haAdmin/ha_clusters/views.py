import ConfigParser
import xmlrpclib

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon import workflows
from openstack_dashboard.dashboards.haAdmin.ha_clusters import tables as project_tables
from openstack_dashboard.dashboards.haAdmin.ha_clusters import workflows as ha_cluster_workflows

config = ConfigParser.RawConfigParser()
config.read('/MOST/HASS/hass.conf')


class Cluster:
    def __init__(self, cluster_name, id, computing_node_number, instance_number):
        self.id = id
        self.cluster_name = cluster_name
        self.computing_node_number = computing_node_number
        self.instance_number = instance_number


class ComputingNode:
    def __init__(self, id, computing_node_name, instance_number):
        self.id = id
        self.computing_node_name = computing_node_name
        self.instance_number = instance_number


class IndexView(tables.DataTableView):
    table_class = project_tables.ClustersTable
    template_name = 'haAdmin/ha_clusters/index.html'
    page_title = _("HA_Clusters")

    def get_data(self):
        authUrl = "http://user:0928759204@127.0.0.1:61209"
        server = xmlrpclib.ServerProxy(authUrl)
        result = server.listCluster()
        clusters = []
        for cluster in result:
            uuid = cluster[0]
            name = cluster[1]
            node_number = 0
            instance_number = 0
            # node_info = server.listNode(uuid)["nodeList"]
            node_info = server.listNode(uuid)
            if node_info["code"] == "succeed":
                node_number = len(node_info["data"]["node_list"])
                # instance_info = server.listInstance(uuid)["instanceList"]
                instance_info = server.listInstance(uuid)
                if instance_info["code"] == "succeed":
                    instance_number = len(instance_info["data"]["instance_list"])
                    clusters.append(Cluster(name, uuid, node_number, instance_number))
        return clusters


class DetailView(tables.DataTableView):
    table_class = project_tables.ClusterDetailTable
    template_name = 'haAdmin/ha_clusters/detail.html'
    page_title = _("HA Cluster (uuid:{{cluster_id}})")

    def get_data(self):
        authUrl = "http://user:0928759204@127.0.0.1:61209"
        server = xmlrpclib.ServerProxy(authUrl)
        result = server.listNode(self.kwargs["cluster_id"])
        if result["code"] == "succeed":  # Success
            computing_nodes = []
            result = result["data"]["node_list"][:]  # filter success code
            if result != "":
                instance_id = 0
                for node in result:
                    name = node[0]
                    full_instance_information = server.listInstance(self.kwargs["cluster_id"])
                    instance_number = self.get_instance_number(name, full_instance_information)
                    computing_nodes.append(ComputingNode(instance_id, name, instance_number))
                    instance_id = instance_id + 1
                return computing_nodes
            else:
                return []
        else:
            return []

    def get_instance_number(self, node_name, data):
        # result, instance_list = data.split(";")
        instance_list = data["data"]["instance_list"]
        result = data["code"]
        instance_number = 0
        # instance_host_list = []
        if result == 'succeed' and instance_list != "":
            for instance in instance_list:
                if node_name == instance[2]:
                    instance_number = instance_number + 1
        return instance_number


class CreateView(workflows.WorkflowView):
    workflow_class = ha_cluster_workflows.CreateHAClusterWorkflow
    template_name = "haAdmin/ha_clusters/create.html"
    page_title = _("Create HA Cluster")


class AddView(workflows.WorkflowView):
    workflow_class = ha_cluster_workflows.AddComputingNodeWorkflow
    template_name = "haAdmin/ha_clusters/add_node.html"
    page_title = _("Add Computing Node")
