from Authenticator import Authenticator
import httplib
import ConfigParser
import json
import time
import logging


config = ConfigParser.RawConfigParser()
config.read('/etc/hass.conf')
REST_host = config.get("RESTful","host")
REST_port = int(config.get("RESTful","port"))
iServCloud_port = "8080"

MESSAGE_OK = 'succeed'
MESSAGE_FAIL = 'failed'

class RESTClient(object):
	_instance = None

	def __init__(self):
		self.authenticator = Authenticator()
		RESTClient._instance = self


	@staticmethod
	def getInstance():
		if not RESTClient._instance:
			RESTClient()
		return RESTClient._instance

	def create_cluster(self, name, node_list=[]):
		data = {"cluster_name": name}
		response = self._get_HASS_response("/HASS/api/cluster", "POST", data)
		if response["code"] == MESSAGE_OK:
			if node_list != []:
				cluster_id = response["data"]["clusterId"]
				return self.add_node(cluster_id, node_list)
			else:
				return response

	def delete_cluster(self, cluster_id):
		return self._get_HASS_response("/HASS/api/cluster?cluster_id=%s" % cluster_id, "DELETE")

	def list_cluster(self):
		return self._get_HASS_response("/HASS/api/clusters", "GET")

	def add_node(self, cluster_id, node_list):
		data = {"cluster_id": cluster_id,"node_list": node_list}
		return self._get_HASS_response("/HASS/api/node", "POST", data)

	def delete_node(self, cluster_id, node_name):
		return self._get_HASS_response("/HASS/api/node?cluster_id=%s&&node_name=%s" %(cluster_id, node_name), "DELETE")

	def list_node(self, cluster_id):
		return self._get_HASS_response("/HASS/api/nodes/%s" % cluster_id, "GET")

	def add_instance(self, cluster_id, instance_id):
		data = {"cluster_id": cluster_id, "instance_id": instance_id}
		return self._get_HASS_response("/HASS/api/instance", "POST", data)

	def delete_instance(self, cluster_id, instance_id):
		return self._get_HASS_response("/HASS/api/instance?cluster_id=%s&&instance_id=%s" % (cluster_id, instance_id), "DELETE")

	def list_instance(self, cluster_id):
		return self._get_HASS_response("/HASS/api/instances/%s" % cluster_id, "GET")

	def recover(self, fail_type, cluster_id, node_name):
		data = {"fail_type": fail_type, "cluster_id": cluster_id, "node_name": node_name}
		return self._get_HASS_response("/HASS/api/recover", "POST", data)

	def updateDB(self):
		return self._get_HASS_response("/HASS/api/updateDB", "GET")

	def send_recover_service_failed(self, node, service):
		subject = "HASS recover service failed"
		data = "recover %s %s failed" % (node.name, service)
		response = self.send_iservcloud_notification(subject, data)
		if response["RESULT"] == 1:
			return False
		return True

	def send_ipmi_failed(self, node):
		subject = "ipmi opereation failed"
		data = "%s ipmi failed" % (node)
		return self.send_iservcloud_notification(subject, data)

	def send_iservcloud_notification(self, subject, content):
		data = {}	
		data["notification_type"] = 1
		data["bulletin_type"] = 3
		data["subject"] = subject
		data["content"] = content
		data["publisher_userid"] = 4
		data["receiver_userid"] = 3
		return self._get_iservcloud_response("/iServCloud/SendNotification", "POST", data)

	def _get_HASS_response(self, endpoint, method, data=None):
		try:
			headers = {'Content-Type' : 'application/json',
					   'X-Auth-Token' : self.authenticator.get_access_token()}
			return self._get_response(REST_host, REST_port, endpoint, method, headers, data)
		except Exception as e:
			print str(e)
			logging.error(str(e))
			return False

	def _get_iservcloud_response(self, endpoint, method, data=None):
		try:
			headers = {'Content-Type' : 'application/json'}
			return  self._get_response(REST_host, iServCloud_port, endpoint, method, headers, data)
		except Exception as e:
			print str(e)
			logging.error(str(e))
			return False

	def _get_response(self, host, port, endpoint, method, headers, data=None):
		conn = httplib.HTTPConnection(host, port, timeout=500)
		headers = headers
		request_data = json.dumps(data)
		conn.request(method, endpoint, body=request_data, headers=headers)
		response = json.loads(conn.getresponse().read())
		conn.close()
		return response

if __name__ == '__main__':
	a = RESTClient.getInstance()
	print a.send_iservcloud_notification("xxx","ggg")