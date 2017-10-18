from NodeInterface import NodeInterface
from Instance import Instance
import paramiko
#from DetectionManager import DetectionManager


class Node (NodeInterface):
	def __init__(self, name, cluster_id):
		super(Node, self).__init__(name , cluster_id)
		self.client = self._create_ssh_client()
		
	def containsInstance(self, instance_id):
		node_instance_list = self.nova_client.getInstanceListByNode(self.name)
		for instance in node_instance_list:
			id = getattr(instance , "id")
			print id
			if id == instance_id:
				return True
		return False

	def getInstanceInfo(self):
		res = []
		for instance in self.protected_instance_list:
			res.append(instance.getInfo())
		return res

	def boot(self):
		return self.ipmi_module.startNode(self.name)

	def shutdown(self):
		return self.ipmi_module.shutOffNode(self.name)

	def reboot(self):
		return self.ipmi_module.rebootNode(self.name)

	def InstanceOverlappingInLibvirt(self, instance):
		return instance.name in self._get_virsh_list()

	def undefineInstance(self, instance):
		stdin, stdout, stderr = self.remote_exec("virsh destroy %s" % instance.name)
		print stdout.read()
		stdin, stdout, stderr = self.remote_exec("virsh undefine %s" % instance.name)
		print stdout.read()

	def _get_virsh_list(self):
		stdin, stdout, stderr = self.remote_exec("virsh list --all")
		return stdout.read()

	def remote_exec(self, cmd):
		if not self.client:
			logging.error("RecoveryManager : cannot create ssh connection")
			return
		stdin, stdout, stderr = self.client.exec_command(cmd)
		return stdin, stdout, stderr

	def _create_ssh_client(self, default_timeout=1):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			client.connect(self.name, username='root', timeout = default_timeout)
			return client
		except Exception as e:
			print "Excpeption : %s" % str(e)
			return None

if __name__ == "__main__":
	a = Node("compute2", "123")
	b = Instance("xx","instance-0000023e","compute2")
	#print a.undefineInstance(b)
	i, out, err = a.remote_exec("echo 123")
	print out.read()
	# print a.remote_exec("cd /home/compute2/Desktop/Hass-Newton/computing_node/ ;python DetectionAgent.py")
	# q,w,e =  a.remote_exec("ps -aux")
	# print w.read()
	# q,w,e =  a.remote_exec("echo 123")
	# print w.read()