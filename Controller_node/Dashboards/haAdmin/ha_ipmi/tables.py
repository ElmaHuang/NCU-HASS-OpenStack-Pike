import ConfigParser
import xmlrpclib

from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import messages
from horizon import tables

config = ConfigParser.RawConfigParser()
config.read('/home/controller/Desktop/HASS/Controller_node/HASS/hass.conf')


# user = config.get("rpc", "rpc_username")
# password = config.get("rpc", "rpc_password")
# port = config.get("rpc", "rpc_bind_port")


class GetNodeInfoAction(tables.LinkAction):
    name = "nodeInfo"
    verbose_name = _("Get Node Info")
    url = "horizon:haAdmin:ha_ipmi:detail"
    classes = ("btn-log",)


class StartNodeAction(tables.BatchAction):
    name = "start"
    classes = ('btn-confirm',)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Start Node",
            u"Start Nodes",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Started Node",
            u"Started Nodes",
            count
        )

    def allowed(self, request, computing_node):
        # check cn's power status
        return (computing_node.state != "up")

    def action(self, request, obj_id):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        result = server.startNode(obj_id)
        if result["code"] == "failed":
            err_msg = result["message"]
            messages.error(request, err_msg)


class RebootNodeAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reboot Node",
            u"Reboot Nodes",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Rebooted Node",
            u"Rebooted Nodes",
            count
        )

    def action(self, request, obj_id):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        result = server.rebootNode(obj_id)
        if result["code"] == "failed":
            err_msg = result["message"]
            messages.error(request, err_msg)


class ShutOffNodeAction(tables.BatchAction):
    name = "shutoff"
    classes = ('btn-reboot',)
    help_text = _("Restarted instances will lose any data"
                  " not saved in persistent storage.")
    action_type = "danger"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Shut off Node",
            u"Shut off Nodes",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Shut offed Node",
            u"Shut offed Nodes",
            count
        )

    def allowd(self, request, computing_node):
        return (computing_node.state != "down")

    def action(self, request, obj_id):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        result = server.shutOffNode(obj_id)
        if result["code"] == "failed":
            err_msg = result["message"]
            messages.error(request, err_msg)


class Ipmi_CN_Table(tables.DataTable):
    STATUS_CHOICES = (
        ("enabled", True),
        ("disabled", False),
        ("up", True),
        ("down", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("enabled", pgettext_lazy("Current status of a Hypervisor",
                                  u"Enabled")),
        ("disabled", pgettext_lazy("Current status of a Hypervisor",
                                   u"Disabled")),
        ("up", pgettext_lazy("Current state of a Hypervisor",
                             u"Up")),
        ("down", pgettext_lazy("Current state of a Hypervisor",
                               u"Down")),
    )

    hostname = tables.WrappingColumn("hypervisor_hostname",
                                     link="horizon:haAdmin:ha_ipmi:detail",
                                     verbose_name=_("Node name"))
    status = tables.Column('status',
                           status=True,
                           status_choices=STATUS_CHOICES,
                           display_choices=STATUS_DISPLAY_CHOICES,
                           verbose_name=_('Nova Compute Status'))
    state = tables.Column('state',
                          status=True,
                          status_choices=STATUS_CHOICES,
                          display_choices=STATUS_DISPLAY_CHOICES,
                          verbose_name=_('Power State'))

    def get_object_id(self, hypervisor):
        return "%s" % (hypervisor.hypervisor_hostname)

    class Meta:
        name = "ha_ipmi_overview"
        verbose_name = _("HA_IPMI")
        # table_actions = (AddInstanceToProtectionAction,)
        row_actions = (StartNodeAction, ShutOffNodeAction, RebootNodeAction, GetNodeInfoAction)
        # row_actions = (StartNodeAction, ShutOffNodeAction, RebootNodeAction)


class IPMINodeTemperatureTable(tables.DataTable):
    sensor = tables.Column("sensor_ID", verbose_name=_("Sensor ID"))

    device = tables.Column("device", verbose_name=_("Device"))

    sensor_type = tables.Column("sensor_type", verbose_name=_("Sensor Type"))

    value = tables.Column("value", verbose_name=_("Value"))

    status = tables.Column("status", verbose_name=_("Status"))

    lc = tables.Column("lower_critical", verbose_name=_("Lower Critical"))

    l = tables.Column("lower_no_critical", verbose_name=_("Lower Non-Critical"))

    u = tables.Column("upper_no_critical", verbose_name=_("Upper Non-Critical"))

    uc = tables.Column("upper_critical", verbose_name=_("Upper Critical"))

    class Meta:
        name = "IPMI_Temp"
        hidden_title = False
        verbose_name = _("Temperature")


class IPMINodeFanTable(tables.DataTable):
    sensor = tables.Column("sensor_ID", verbose_name=_("Sensor ID"))

    device = tables.Column("device", verbose_name=_("Device"))

    sensor_type = tables.Column("sensor_type", verbose_name=_("Sensor Type"))

    value = tables.Column("value", verbose_name=_("Value"))

    status = tables.Column("status", verbose_name=_("Status"))

    lc = tables.Column("lower_critical", verbose_name=_("Lower Critical"))

    l = tables.Column("lower_no_critical", verbose_name=_("Lower Non-Critical"))

    u = tables.Column("upper_no_critical", verbose_name=_("Upper Non-Critical"))

    uc = tables.Column("upper_critical", verbose_name=_("Upper Critical"))

    class Meta:
        name = "IPMI_Fan"
        hidden_title = False
        verbose_name = _("Fan")
