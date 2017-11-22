import socket
import subprocess
import State
import time
from IPMIModule import IPMIManager

class Detector(object):
	def __init__(self, node, port):
		self.node = node.name
		self.ipmi_status = node.ipmi_status
		self.ipmi_manager = IPMIManager()
		self.port = port
		self.sock = None
		self.connect()

	def connect(self):
		#connect to FA
		try:
			print "["+self.node+"] create socket connection"
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sock.setblocking(0)
			self.sock.settimeout(0.5)
			self.sock.connect((self.node, self.port))
			#time.sleep(5)
		except Exception as e:
			print str(e)
			print "Init ["+self.node+"] connection failed"

	def checkNetworkStatus(self):
		try:
			response = subprocess.check_output(['timeout', '0.2', 'ping', '-c', '1', self.node], stderr=subprocess.STDOUT, universal_newlines=True)
		except subprocess.CalledProcessError:
			return State.NETWORK_FAIL
		return State.HEALTH

	def checkServiceStatus(self):
		try:
			line = "polling request"
			self.sock.sendall(line)
			data, addr = self.sock.recvfrom(1024)
			if data == "OK":
				return State.HEALTH
			elif "error" in data :
				print data
				print "["+self.node+"]service Failed"
			elif not data:
				print "["+self.node+"]no ACK"
			else:
				print "["+self.node+"]Receive:"+data
			return State.SERVICE_FAIL
		except Exception as e:
			fail_services = "agents"
			print "["+self.node+"] connection failed"
			self.sock.connect((self.node, self.port))
			return State.SERVICE_FAIL

	def checkPowerStatus(self):
		if not self.ipmi_status:
			return State.HEALTH
		status = self.ipmi_manager.getPowerStatus(self.node)
		if status == "OK":
			return State.HEALTH
		return State.POWER_FAIL

	def checkOSStatus(self):
		if not self.ipmi_status:
			return State.HEALTH
		status = self.ipmi_manager.getOSStatus_new(self.node)
		if status == "OK":
			return State.HEALTH
		return State.OS_FAIL

	def checkSensorStatus(self):
		if not self.ipmi_status:
			return State.HEALTH
		status = self.ipmi_manager.getSensorStatus(self.node)
		if status == "OK":
			return State.HEALTH
		return State.SENSOR_FAIL

	def getFailServices(self):
		try:
			line = "polling request"
			self.sock.sendall(line)
			data, addr = self.sock.recvfrom(1024)
			if data != "OK":
				return data
		except Exception as e:
			return "agents"

