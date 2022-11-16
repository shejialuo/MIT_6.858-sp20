from debug import *
from zoodb import *
import rpclib

sys.path.append(os.getcwd())
import readconf

def transfer(sender, recipient, zoobars, token=""):
    host = readconf.read_conf().lookup_host('bank')
    with rpclib.client_connect(host) as c:
        kwargs = {'sender':sender,'recipient':recipient, 'zoobars': zoobars, 'token': token}
        ret = c.call('transfer', **kwargs)
        return ret

def balance(username):
    host = readconf.read_conf().lookup_host('bank')
    with rpclib.client_connect(host) as c:
        kwargs = {'username':username}
        ret = c.call('balance', **kwargs)
        return ret

def register(username):
    host = readconf.read_conf().lookup_host('bank')
    with rpclib.client_connect(host) as c:
        kwargs = {'username':username}
        ret = c.call('register', **kwargs)
        return ret

def get_log(username):
    host = readconf.read_conf().lookup_host('bank')
    with rpclib.client_connect(host) as c:
        kwargs = {'username':username}
        ret = c.call('get_log', **kwargs)
        return ret
