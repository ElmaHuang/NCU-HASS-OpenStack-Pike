class Schedule():        
    def default(self, node_list, fail_node= ""):
        import random
        target_list = [host for host in hostList if host != failednode]
        host = random.choice(target_list)
        print "target host", host
        return host
        
def main():

    test = Schedule()
    host_list = ["host1", "host2"]
    print test.default(host_list, "host2")

if __name__ == "__main__":
    main()
