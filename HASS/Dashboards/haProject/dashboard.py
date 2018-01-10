import horizon
from django.utils.translation import ugettext_lazy as _


class HA_Project(horizon.Dashboard):
    name = _("HA Project")
    slug = "haProject"
    default_panel = 'ha_instances'
    panels = ('ha_instances',)


horizon.register(HA_Project)
