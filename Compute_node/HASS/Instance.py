from NovaClient import NovaClient

class Instance(object):
    def __init__(self, cluster_id, ha_instance):
        self.nova_client = NovaClient.getInstance()
        self.cluster_id = cluster_id
        self.id = ha_instance[0]
        self.name = ha_instance[1]
        self.host = ha_instance[2]
        self.status = ha_instance[3]
        self.network = ha_instance[4]
        self.network_self = []
        self.network_provider = []
        self.update_network()
        print "cluster_id:", self.cluster_id, "id:", self.id, " name:", self.name, " host:", self.host, " status:", self.status, " network_s:", self.network_self, "p:", self.network_provider

    def update_network(self):
        print "update net"
        # {'selfservice':", "['192.168.1.8',", "'192.168.0.212']}
        for router_name, ip_list in self.network.iteritems():
            for ip in ip_list:
                status = self._checkExternalNetwork(ip)
                if status:
                    self.network_provider.append(ip)
                else:
                    self.network_self.append(ip)
        # if "selfservice" in self.network:
        #     self.network_self = self.network["selfservice"][0]
        #     if self.network["selfservice"] > 1:
        #         self.network_provider = self.network["selfservice"][0]
        # if "provider" in self.network:
        #     self.network_provider = self.network["provider"]
            # self.network

    def _checkExternalNetwork(self,ip):
        ext_ip = self.nova_client.getInstanceExternalNetwork(ip)
        if not ext_ip:
            return False
        return True
