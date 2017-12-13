#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#   This is a class maintains node data structure.
##########################################################

from NodeInterface import NodeInterface
import logging
import paramiko
from Instance import Instance

class Node (NodeInterface):
	def __init__(self, name, cluster_id):
		super(Node, self).__init__(name , cluster_id)
		self.client = self._create_ssh_client()
		
	def containsInstance(self, instance_id):
		#node_instance_list = self.nova_client.getInstanceListByNode(self.name)
		host = self.nova_client.getInstanceHost(instance_id)
		#print host
		#print self.name
		if host == self.name:
			return True
		return False

	def start(self):
		return self.ipmi.startNode(self.name)

	def shutoff(self):
		return self.ipmi.shutOffNode(self.name)

	def reboot(self):
		return self.ipmi.rebootNode(self.name)

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
		if not self.check_connection():
			logging.error("ssh connection lost")
			self.client = self._create_ssh_client()
			logging.info("ssh connection re-established")
		stdin, stdout, stderr = self.client.exec_command(cmd, timeout = 5)
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

	def check_connection(self):
		try:
			self.client.exec_command('ls', timeout=5)
			return True
		except Exception as e:
			print "Connection lost : %s" % str(e)
			return False

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
