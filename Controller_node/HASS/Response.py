#########################################################
#:Date: 2017/12/13
#:Version: 1
#:Authors:
#    - Elma Huang <huanghuei0206@gmail.com>
#    - LSC <sclee@g.ncu.edu.tw>
#:Python_Version: 2.7
#:Platform: Unix
#:Description:
#	This is a result data structure.
##########################################################


class Response(object):
    def __init__(self, code, message = None, data = None):
        self.code = code
        self.message = message
        self.data = data
