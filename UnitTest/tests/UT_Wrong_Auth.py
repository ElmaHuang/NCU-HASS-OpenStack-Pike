import Preprocess
import Postprocess
import xmlrpclib
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('hass.conf')
wrong_auth = "http://" + "none" + ":" + config.get("rpc", "rpc_password") + "@127.0.0.1:" + config.get("rpc",
                                                                                                       "rpc_bind_port")


def run():
    try:
        server = xmlrpclib.ServerProxy(wrong_auth)
        response = server.test_auth_response()
        if response == "auth success":
            return False
        return True
    except Exception as e:
        return True
    finally:
        Postprocess.server_stop()
