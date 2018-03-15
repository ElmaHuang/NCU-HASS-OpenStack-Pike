from flask import Flask
from flask import request
from flask import jsonify
from flask import abort, make_response
import xmlrpclib
import sys

app = Flask(__name__)


rpc_username = "user"
rpc_password = "0928759204"
rpc_port = 61209


auth_url = "http://%s:%s@127.0.0.1:%s" % (rpc_username, rpc_password, rpc_port)
server = xmlrpclib.ServerProxy(auth_url)

# for POST method, need to specify the 'Content-Type = application/json' in the requeset header.
# for GET method, need to specify the parameter after the url.

@app.errorhandler(400)
def lack_arguments(error):
	return make_response(jsonify({'message':"lack some arguments, please check the documentation.","code":"failed","data":None}), 400)

@app.route("/")
def hello():
    return "hello"
@app.route("/HASS/api/cluster", methods=['POST'])
def create_cluster():
    if not request.json or \
       "cluster_name" not in request.json:
        abort(400)
    cluster_name = request.json["cluster_name"]
    res = server.createCluster(cluster_name)
    return jsonify(res)

@app.route("/HASS/api/cluster", methods=['DELETE'])
def delete_cluster():
    if not request.json or \
       "cluster_id" not in request.json:
	abort(400)
    cluster_id = request.json["cluster_id"]
    res = server.deleteCluster(cluster_id)
    return jsonify(res)

@app.route("/HASS/api/clusters", methods=['GET'])
def list_cluster():
    cluster_list = server.listCluster()
    return jsonify(cluster_list)

@app.route("/HASS/api/node", methods=['POST'])
def add_node():
    if not request.json or \
       "cluster_id" not in request.json or \
       "node_list" not in request.json:
	abort(400)
    cluster_id = request.json["cluster_id"]
    node_list = request.json["node_list"]
    res = server.addNode(cluster_id, node_list)
    return jsonify(res)

@app.route("/HASS/api/node", methods=['DELETE'])
def delete_node():
    if not request.json or \
       "cluster_id" not in request.json or \
       "node_name" not in request.json:
 	abort(400)
    cluster_id = request.json["cluster_id"]
    node_name = request.json["node_name"]
    res = server.deleteNode(cluster_id, node_name)
    return jsonify(res)

@app.route("/HASS/api/nodes/<string:cluster_id>", methods=['GET'])
def list_node(cluster_id):
    res = server.listNode(cluster_id)
    return jsonify(res)

@app.route("/HASS/api/instance", methods=['POST'])
def add_instance():
    if not request.json or \
       "cluster_id" not in request.json or \
       "instance_id" not in request.json:
	abort(400)
    cluster_id = request.json["cluster_id"]
    instance_id = request.json["instance_id"]
    res = server.addInstance(cluster_id, instance_id)
    return jsonify(res)

@app.route("/HASS/api/instance", methods=['DELETE'])
def delete_instance():
    if not request.json or \
       "cluster_id" not in request.json or \
       "instance_id" not in request.json:
	abort(400)
    cluster_id = request.json["cluster_id"]
    instance_id = request.json["instance_id"]
    res = server.deleteInstance(cluster_id, instance_id)
    return jsonify(res)

@app.route("/HASS/api/instances/<string:cluster_id>", methods=['GET'])
def list_instance(cluster_id):
    res = server.listInstance(cluster_id)
    return jsonify(res)


if __name__ == '__main__':
    host = sys.argv[1] # specified by user
    port = 9999 # specified by user
    if len(sys.argv) > 3:
	port = sys.argv[2]
    app.run(debug=True, port=int(port), host=host)
