import Preprocess
import Postprocess
import xmlrpclib
import ConfigParser

no_auth = ""


def run():
    try:
        server = xmlrpclib.ServerProxy(no_auth)
        response = server.test_auth_response()
        if response == "auth success":
            return False
        return True
    except Exception as e:
        return True
    finally:
        Postprocess.server_stop()
