from functools import wraps
from flask import Flask
from flask import request
from flask import jsonify
from flask import abort, make_response
import httplib
import json
import threading
import xmlrpclib
import sys
import ConfigParser
from Response import Response

# for POST method, need to specify the 'Content-Type = application/json' in the request header.
# for GET method, need to specify the parameter after the url.

app = Flask(__name__)

config = ConfigParser.RawConfigParser()
config.read('hass.conf')

rpc_username = config.get("rpc","rpc_username")
rpc_password = config.get("rpc","rpc_password")
rpc_port = int(config.get("rpc","rpc_bind_port"))

REST_host = config.get("RESTful","host")
REST_port = int(config.get("RESTful","port"))

keystone_port = int(config.get("keystone_auth","port"))

openstack_user_name = config.get("openstack", "openstack_admin_account")
openstack_domain = config.get("openstack", "openstack_user_domain_id")
openstack_password = config.get("openstack", "openstack_admin_password")

HASS = None
authenticator = None

def _convert_res_to_JSON(response):
  return json.dumps(response.__dict__)

class Authenticator(object):
  def __init__(self):
    self.access_token = self.get_access_token()

  def success(self, token):
    return self.is_token_valid(token)

  def get_access_token(self):
    try:
      data = '{ "auth": { "identity": { "methods": [ "password" ], "password": { "user": { "name": \"%s\", "domain": { "name": \"%s\" }, "password": \"%s\" } } } } }' % (openstack_user_name, openstack_domain, openstack_password)
      headers = {"Content-Type": "application/json"}
      http_client = httplib.HTTPConnection(REST_host, keystone_port, timeout=30)
      http_client.request("POST", "/v3/auth/tokens", body=data, headers=headers)
      return http_client.getresponse().getheaders()[1][1]
    finally:
      if http_client:
        http_client.close()

  def refresh_access_token(self):
    self.access_token = self.get_access_token()

  def is_token_valid(self, token):
    if not token:
      return False
    try:
      headers = {"X-Auth-Token": self.access_token, "X-Subject-Token": token}
      http_client = httplib.HTTPConnection(REST_host, keystone_port, timeout=30)
      http_client.request("GET", "/v3/auth/tokens", headers=headers)
      response = http_client.getresponse()
      if response.status == httplib.UNAUTHORIZED:
        self.refresh_access_token()
        return self.is_token_valid(token)
      map_response = json.loads(response.read())
      if "error" in map_response and \
        map_response["error"]["code"] == httplib.NOT_FOUND:
        return False
      return True
    finally:
      if http_client:
        http_client.close()

class RESTfulThread(threading.Thread):
  def __init__(self, input_HASS):
    threading.Thread.__init__(self)
    global HASS
    global authenticator
    HASS = input_HASS
    authenticator = Authenticator()

  def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
      if "X-Auth-Token" not in request.headers:
        abort(401)
      token = request.headers["X-Auth-Token"]
      if not authenticator.success(token):
        abort(401)
      print "RESTful request in."
      return f(*args, **kwargs)
    return decorated

  def run(self):
    print "RESTful server ready! host : %s, port : %s\n" % (REST_host, REST_port)
    app.run(port=REST_port, host=REST_host)

  @app.errorhandler(Exception)
  def global_exception_handle(error):
    print str(error)
    return make_response(jsonify({'message':"exception happens during request operation." ,"code":"failed","data":str(error)}), 500)

  @app.errorhandler(400)
  def lack_arguments(error):
    return make_response(jsonify({'message':"lack some arguments, please check the documentation.","code":"failed","data":400}), 400)

  @app.errorhandler(401)
  def auth_fail(error):
    return make_response(jsonify({'message':"The request you have made requires authentication.","code":"failed","data":401}), 401)

  @app.route("/HASS/api/cluster", methods=['POST'])
  @requires_auth
  def create_cluster():
    if not request.json or \
      "cluster_name" not in request.json:
        abort(400)
    cluster_name = request.json["cluster_name"]
    res = HASS.createCluster(cluster_name)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/cluster", methods=['DELETE'])
  @requires_auth
  def delete_cluster():
    if not request.args.get("cluster_id"):
      abort(400)
    cluster_id = request.args.get("cluster_id")
    res = HASS.deleteCluster(cluster_id)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/clusters", methods=['GET'])
  @requires_auth
  def list_cluster():
    res = HASS.listCluster()
    if res != None:
      res = Response(code="succeed",
                     message="get cluster list success",
                     data=res)
      return _convert_res_to_JSON(res)
    else:
      res = Response(code="failed",
                     message="get cluster list failed",
                     data=None)
      return _convert_res_to_JSON(res)

  @app.route("/HASS/api/node", methods=['POST'])
  @requires_auth
  def add_node():
    if not request.json or \
    "cluster_id" not in request.json or \
    "node_list" not in request.json:
        abort(400)
    cluster_id = request.json["cluster_id"]
    node_list = request.json["node_list"]
    res = HASS.addNode(cluster_id, node_list)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/node", methods=['DELETE'])
  @requires_auth
  def delete_node():
    if not request.args.get("cluster_id") or \
       not request.args.get("node_name"):
       abort(400)
    cluster_id = request.args.get("cluster_id")
    node_name = request.args.get("node_name")
    res = HASS.deleteNode(cluster_id, node_name)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/nodes/<string:cluster_id>", methods=['GET'])
  @requires_auth
  def list_node(cluster_id):
    res = HASS.listNode(cluster_id)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/instance", methods=['POST'])
  @requires_auth
  def add_instance():
    if not request.json or \
      "cluster_id" not in request.json or \
      "instance_id" not in request.json:
        abort(400)
    cluster_id = request.json["cluster_id"]
    instance_id = request.json["instance_id"]
    res = HASS.addInstance(cluster_id, instance_id)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/instance", methods=['DELETE'])
  @requires_auth
  def delete_instance():
    if not request.args.get("cluster_id") or \
       not request.args.get("instance_id"):
       abort(400)
    cluster_id = request.args.get("cluster_id")
    instance_id = request.args.get("instance_id")
    res = HASS.deleteInstance(cluster_id, instance_id)
    return _convert_res_to_JSON(res)

  @app.route("/HASS/api/instances/<string:cluster_id>", methods=['GET'])
  @requires_auth
  def list_instance(cluster_id):
    res = HASS.listInstance(cluster_id)
    return _convert_res_to_JSON(res)

if __name__ == '__main__':
  pass