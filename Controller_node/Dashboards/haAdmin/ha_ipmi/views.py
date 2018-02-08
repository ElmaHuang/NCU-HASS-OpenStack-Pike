import ConfigParser
import xmlrpclib

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon.utils import functions as utils
from openstack_dashboard.api import nova
from openstack_dashboard.dashboards.haAdmin.ha_ipmi import tables as project_tables

config = ConfigParser.RawConfigParser()
config.read('/home/controller/Desktop/HASS/Controller_node/HASS/hass.conf')


# user = config.get("rpc", "rpc_username")
# password = config.get("rpc", "rpc_password")
# port = config.get("rpc", "rpc_bind_port")


class Temperature:
    def __init__(self, table_index, sensor_id, device, sensor_type, value, status, lower_critical, lower, upper,
                 upper_critical):
        self.id = table_index
        self.sensor_ID = sensor_id
        self.device = device
        self.sensor_type = sensor_type
        self.value = value
        self.status = status
        self.lower_critical = lower_critical
        self.lower_no_critical = lower
        self.upper_no_critical = upper
        self.upper_critical = upper_critical


class Fan:
    def __init__(self, table_index, sensor_id, device, sensor_type, value, status, lower_critical, lower, upper,
                 upper_critical):
        self.id = table_index
        self.sensor_ID = sensor_id
        self.device = device
        self.sensor_type = sensor_type
        self.value = value
        self.status = status
        self.lower_critical = lower_critical
        self.lower_no_critical = lower
        self.upper_no_critical = upper
        self.upper_critical = upper_critical


class IndexView(tables.DataTableView):
    table_class = project_tables.Ipmi_CN_Table
    template_name = 'haAdmin/ha_ipmi/index.html'
    page_title = _("HA_IPMI_Node")

    def get_data(self):
        hypervisors = []
        try:
            hypervisors = nova.hypervisor_list(self.request)
            hypervisors.sort(key=utils.natural_sort('hypervisor_hostname'))
        except Exception:
            exceptions.handle(self.request, _(
                'Unable to retrieve hypervisor Controller_node/Dashboards/haAdmin/ha_ipmi/views.py:61information.'))
        return hypervisors


class DetailView(tables.MultiTableView):
    table_classes = (project_tables.IPMINodeTemperatureTable, project_tables.IPMINodeFanTable)
    template_name = 'haAdmin/ha_ipmi/detail.html'
    page_title = _("IPMI-based Node : {{node_id}}")
    result = None

    def get_IPMI_Temp_data(self):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        self.result = server.getAllInfoOfNode(self.kwargs["node_id"])
        temp_data = []
        if self.result["code"] == "succeed":
            table_index = 0
            data_list = self.result["data"]["info"]
            # [
            # ['Temp (0xe)', 'Processor', 'Temperature', '41 (+/- 1) degrees C', 'ok', '3.000', '8.000', 95.000', '100.000'],
            # ['Inlet Temp (0x4)', 'System Board', 'Temperature', '19 (+/- 1) degreesC', 'ok', '-7.000', '3.000', '37.000', '42.000'],
            # ['Fan1 (0x30)', 'System Board', 'Fan', '100 (+/- 120) RPM', 'ok', '240.000', '360.000', 'na', 'na'],
            # ['Fan2 (0x31)', 'System Board', 'Fan', '1080 (+/- 120) RPM', 'ok', '240.000', '360.000', 'na', 'na']
            # ]
            for data in data_list:
                # [sensor_id, device, sensor_type, value, status, lower_critical, lower, upper, upper_critical]
                sensor_id = data[0]
                device = data[1]
                sensor_type = data[2]
                value = data[3]
                status = data[4]
                lower_critical = data[5]
                lower = data[6]
                upper = data[7]
                upper_critical = data[8]
                if "Temperature" in sensor_type:
                    temp_data.append(
                        Temperature(table_index, sensor_id, device, sensor_type, value, status, lower_critical, lower,
                                    upper, upper_critical))
                    table_index += 1
        return temp_data

    def get_IPMI_Fan_data(self):
        fan_data = []
        if self.result["code"] == "succeed":
            table_index = 0
            data_list = self.result["data"]["info"]
            for data in data_list:
                # [sensor_id, device, sensor_type, value, status, lower_critical, lower, upper, upper_critical]
                sensor_id = data[0]
                device = data[1]
                sensor_type = data[2]
                value = data[3]
                status = data[4]
                lower_critical = data[5]
                lower = data[6]
                upper = data[7]
                upper_critical = data[8]
                if "Fan" in sensor_type:
                    fan_data.append(
                        Fan(table_index, sensor_id, device, sensor_type, value, status, lower_critical, lower,
                            upper, upper_critical))
                    table_index += 1
        return fan_data
