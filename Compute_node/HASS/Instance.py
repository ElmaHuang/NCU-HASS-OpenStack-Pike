class Instance(object):
    def __init__(self, cluster_id, ha_instance):
        #self.ha_instance = ha_instance
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
        if "selfservice" in self.network:
            self.network_self = self.network["selfservice"]
        if "provider" in self.network:
            self.network_provider = self.network["provider"]
            # self.network
