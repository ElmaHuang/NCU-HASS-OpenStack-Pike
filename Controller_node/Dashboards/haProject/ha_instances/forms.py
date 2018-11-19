# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Views for managing Neutron Routers.
"""
import ConfigParser
import logging
import random
import xmlrpclib

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances \
    import tables as project_tables

LOG = logging.getLogger(__name__)
config = ConfigParser.RawConfigParser()
config.read('/home/controller/Desktop/HASS/Controller_node/HASS/hass.conf')


# user = config.get("rpc", "rpc_username")
# password = config.get("rpc", "rpc_password")
# port = config.get("rpc", "rpc_bind_port")


class AddForm(forms.SelfHandlingForm):
    instance_id = forms.ChoiceField(label=_("Instance"))

    def __init__(self, request, *args, **kwargs):
        super(AddForm, self).__init__(request, *args, **kwargs)
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        instance_choices = [('', _("Select an instance"))]

        instances = []
        marker = self.request.GET.get(
            project_tables.InstancesTable._meta.pagination_param, None)
        # search_opts = self.get_filters({'marker': marker, 'paginate': True})
        try:
            instances, self._more = api.nova.server_list(
                self.request)
            # search_opts=search_opts)
        except Exception:
            self._more = False
            exceptions.handle(self.request,
                              _('Unable to retrieve instance list.'))

        for instance in instances:
            instance_choices.append((instance.id, instance.name))
        self.fields['instance_id'].choices = instance_choices

    def handle(self, request, data):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)

        clusters = server.listCluster()

        if not clusters:
            err_msg = _("There is no available HA Cluster in system.")
            messages.error(request, err_msg)
            return False

        random_cluster = random.choice(clusters)
        result = server.addInstance(random_cluster[0], data['instance_id'])
        if result["code"] == 'failed':
            err_msg = _(result["message"])
            messages.error(request, err_msg)
            return False
        try:
            instance_name = api.nova.server_get(request, data['instance_id']).name
            success_message = _('Add Instance:%s to HA Cluster.' % instance_name)
            messages.success(request, success_message)
        except Exception:
            msg = _('Unable to retrieve instance.')
            exceptions.handle(self.request, msg)
        return True


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"), required=False,
                           widget=forms.TextInput(
                               attrs={'readonly': 'readonly'}))
    protection = forms.ChoiceField(choices=[(True, _('Protected')),
                                            (False, _('Non-Protected'))],
                                   label=_("Protection"))
    instance_id = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly'}))
    # admin_state = forms.ChoiceField(choices=[(True, _('UP')),
    #                                         (False, _('DOWN'))],
    #                                label=_("Admin State"))
    # router_id = forms.CharField(label=_("ID"),
    #                            widget=forms.TextInput(
    #                                attrs={'readonly': 'readonly'}))
    # mode = forms.ChoiceField(label=_("Router Type"))

    redirect_url = reverse_lazy('horizon:haProject:ha_instances:index')

    def __init__(self, request, *args, **kwargs):
        super(UpdateForm, self).__init__(request, *args, **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        self.fields['instance_id'].initial = instance_id

    def handle(self, request, data):
        authUrl = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                                   "rpc_password") + "@127.0.0.1:" + config.get(
            "rpc", "rpc_bind_port")
        server = xmlrpclib.ServerProxy(authUrl)
        err_msg = _('Unable to remove protection of HA instance: %s ' % data['name'])
        if data['protection'] == 'False':
            cluster_id = self.get_cluster_by_instance(server, data['instance_id'])
            result = server.deleteInstance(cluster_id, data['instance_id'])
            if result["code"] == 'failed':
                err_msg = result["message"]
                messages.error(request, err_msg)
                return False
            try:
                instance = api.nova.server_get(self.request, data['instance_id'])
            except Exception:
                redirect = reverse("horizon:haProject:ha_instances:index")
                msg = _('Unable to retrieve instance details.')
                exceptions.handle(self.request, msg, redirect=redirect)
                return False
            success_message = _('Deleted Instance:%s from HA Cluster.' % instance.name)
            messages.success(request, success_message)
        return True

    def get_cluster_by_instance(self, server, instance_id):
        clusters = server.listCluster()
        cluster_uuid = ""
        for cluster in clusters:
            uuid = cluster[0]
            _ha_instances = server.listInstance(uuid)
            # result, ha_instances = _ha_instances.split(";")
            result = _ha_instances["code"]
            ha_instances = _ha_instances["data"]["instance_list"]
            if result == 'succeed':
                res = []
                # ha_instances = ha_instances.split(",")
                for _instance in ha_instances:
                    res.append(_instance[0])
                for _inst_id in ha_instances:
                    if instance_id in _inst_id:
                        cluster_uuid = uuid
        return cluster_uuid
