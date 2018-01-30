import horizon
from django.utils.translation import ugettext_lazy as _


class HA_Project(horizon.Dashboard):
    name = _("HA Project")
    slug = "haProject"
    default_panel = 'ha_instances'
    panels = ('ha_instances',)
    permissions = ('openstack.roles.user',)


horizon.register(HA_Project)
