# coding: utf-8
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
auth = v3.Password(auth_url = 'http://controller:5000/v3',username = 'admin',password = '0928759204' , project_name = 'admin',user_domain_name = 'default',project_domain_name = 'default')
sess = session.Session(auth = auth)
novaClient = client.Client(2.25 , session = sess)

