class RecoveryInstance():
    def __init__(self):
        pass

    def rebootInstance(self):
        # reboot vm
        last_fail = Configure.Vm_lastfail_messages[0][0]
        command = Configure.Rebootvm_command_format % (vm_name)
        node_ip = ClusterInfo.getIPAddress()
        result = self.__connect(node_ip, Configure.VMManager_port, command)
        if result != Configure.Rebootvm_success:
            last_fail = Configure.Vm_lastfail_messages[1][0]
        # record the last fail of vm into clusterInfo file
        record_command = Configure.Update_vm_status_command_format % (vm_name, last_fail)
        for i in range(Configure.Max_update_vm_status_times):
            node_ip = ClusterInfo.getNodeIP(ClusterInfo.getPrimaryNodeName())
            result = self.__connect(node_ip, Configure.CommandHandler_port, record_command)
            if result == Configure.Update_vm_status_success:
                break

    def rebuildInstance(self):
        pass
