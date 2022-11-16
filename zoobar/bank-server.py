#!/usr/bin/env python3

import rpclib
import sys
import bank
from debug import *

class BankRpcServer(rpclib.RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, token):
        return bank.transfer(sender, recipient, zoobars, token)
    def rpc_balance(self, username):
        return bank.balance(username)
    def rpc_register(self, username):
        return bank.register(username)
    def rpc_get_log(self, username):
        return bank.get_log(username)

if len(sys.argv) != 2:
    print(sys.argv[0], "too few args")

s = BankRpcServer()
s.run_fork(sys.argv[1])
