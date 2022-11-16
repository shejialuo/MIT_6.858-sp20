from debug import *
from zoodb import *
import rpclib

sys.path.append(os.getcwd())
import readconf

def login(username, password):
    host = readconf.read_conf().lookup_host('auth')
    with rpclib.client_connect(host) as c:
        kwargs = {'username':username,'password':password}
        ret = c.call('login', **kwargs)
        return ret

def register(username, password):
    host = readconf.read_conf().lookup_host('auth')
    with rpclib.client_connect(host) as c:
        kwargs = {'username':username,'password':password}
        ret = c.call('register', **kwargs)
        return ret

def check_token(username, token):
    host = readconf.read_conf().lookup_host('auth')

    with rpclib.client_connect(host) as c:
        kwargs = {'username':username,'token':token}
        ret = c.call('check_token', **kwargs)
        return ret
