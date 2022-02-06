#!/usr/bin/env python3

import base64
import rpclib
import sys
import os
import sandboxlib
import hashlib
import socket
import bank
import zoodb

sys.path.append(os.getcwd())
import readconf

from debug import *

## Cache packages that the sandboxed code might want to import
import time
import errno

class ProfileAPIServer(rpclib.RpcServer):
    def __init__(self, user, visitor, pcode, ct):
        self.user = user
        self.visitor = visitor
        self.pcode = pcode
        self.ct = ct

    def rpc_get_self(self):
        return self.user

    def rpc_get_visitor(self):
        return self.visitor

    def rpc_get_xfers(self, username):
        return bank_client.get_log(username)

    def rpc_get_user_info(self, username):
        return { 'username': self.user,
                 'profile': self.pcode,
                 'zoobars': bank.balance(username),
               }

    def rpc_xfer(self, target, zoobars):
        bank.transfer(self.user, target, zoobars)

def run_profile(pcode, profile_api_client):
    globals = {'api': profile_api_client}
    exec(pcode, globals)

class ProfileServer(rpclib.RpcServer):
    def rpc_run(self, pcode, user, visitor):
        uid = 0

        userdir = '/tmp'

        (sa, sb) = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        pid = os.fork()
        if pid == 0:
            if os.fork() <= 0:
                sa.close()
                ct = readconf.read_conf()
                ProfileAPIServer(user, visitor, pcode, ct).run_sock(sb)
                sys.exit(0)
            else:
                sys.exit(0)
        sb.close()
        os.waitpid(pid, 0)

        sandbox = sandboxlib.Sandbox(userdir, uid, '/tmp/lockfile')
        with rpclib.RpcClient(sa) as profile_api_client:
            return sandbox.run(lambda: run_profile(pcode, profile_api_client))

if len(sys.argv) != 2:
    print(sys.argv[0], "too few args")

s = ProfileServer()
s.run_fork(sys.argv[1])
