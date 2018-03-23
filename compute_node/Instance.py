class Instance(object):
    def __init__(self, ha_instance):
        self.ha_instance = ha_instance
        self.id = None
        self.name = None
        self.host = None
        self.status = None
        self.network_self = []
        self.network_provider = []
        self.main()

    def main(self):
        self.id = self.ha_instance["id"]
        self.name = self.ha_instance["name"]
        self.host = self.ha_instance["host"]
        self.status = self.ha_instance["status"]
        self.update_network()
        print "id:", self.id, " name:", self.name, " host:", self.host, " status:", self.status, " network_s:", self.network_self, "p:", self.network_provider

    def update_network(self):
        # {'selfservice':", "['192.168.1.8',", "'192.168.0.212']}
        network = self.ha_instance["network"]
        if "selfservice" in network:
            self.network_self = network["selfservice"]
        if "provider" in network:
            self.network_provider = self.ha_instance["network"]["provider"]
            # self.network


if __name__ == '__main__':
    a = Instance()
