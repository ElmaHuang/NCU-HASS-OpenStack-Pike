import Preprocess
import Postprocess
import xmlrpclib
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('hass.conf')
auth = "http://" + config.get("rpc", "rpc_username") + ":" + config.get("rpc",
                                                                        "rpc_password") + "@127.0.0.1:" + config.get(
    "rpc", "rpc_bind_port")


def run():
    try:
        Preprocess.server_start(False)
        server = xmlrpclib.ServerProxy(auth)
        response = server.test_auth_response()
        if response == "auth success":
            return True
        return False
    except Exception as e:
        print str(e)
        return False
    finally:
        Postprocess.server_stop()
