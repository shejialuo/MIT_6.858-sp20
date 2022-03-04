#!/usr/bin/env python3

import rpclib
import sys
from debug import *

class EchoRpcServer(rpclib.RpcServer):
    def rpc_echo(self, s):
        return 'You said "%s" from %s' % (s, self.caller)

(_, dummy_zookld_fd, sockpath) = sys.argv

s = EchoRpcServer()
s.run_sockpath_fork(sockpath)
