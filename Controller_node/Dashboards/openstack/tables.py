# /usr/share/openstack-dashboard/openstack_dashboard/dashboards/project/instances/tables.py
'''
...
...

'''


# 811 line
class StopInstance(policy.PolicyTargetMixin, tables.BatchAction):
    name = "stop"
    policy_rules = (("compute", "os_compute_api:servers:stop"),)
    # fix 814 line
    help_text = _("The instance(s) will be shut off. And it(they) is(are) still protected.")
    action_type = "danger"

    @staticmethod
    def action_present(count):
        """

        :param count: 
        :return: 
        """
        return npgettext_lazy(
            "Action to perform (the instance is currently running)",
            u"Shut Off Instance",
            u"Shut Off Instances",
            count
            )

    @staticmethod
    def action_past(count):
        """

        :param count: 
        :return: 
        """
        return npgettext_lazy(
            "Past action (the instance is currently already Shut Off)",
            u"Shut Off Instance",
            u"Shut Off Instances",
            count
            )

    def allowed(self, request, instance):
        """

        :param request: 
        :param instance: 
        :return: 
        """
        return ((instance is None)
                or ((get_power_state(instance) in ("RUNNING", "SUSPENDED"))
                    and not is_deleting(instance)))

    def action(self, request, obj_id):
        """

        :param request: 
        :param obj_id: 
        """
        api.nova.server_stop(request, obj_id)
