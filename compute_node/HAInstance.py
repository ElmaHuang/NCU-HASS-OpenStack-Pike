class HAInstance():
    instance_list = None

    @staticmethod
    def init():
        HAInstance.instance_list = {}

    @staticmethod
    def addInstance(ha_instance):
        id = ha_instance.id
        HAInstance.instance_list[id] = ha_instance

    @staticmethod
    def getInstanceList():
        return HAInstance.instance_list

    @staticmethod
    def getInstance(name):
        for id, instance in HAInstance.instance_list.iteritems():
            if instance.name == name:
                return instance
