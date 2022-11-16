from zoodb import *
from debug import *

import time
import auth_client

def transfer(sender, recipient, zoobars, token):
    bank_db = bank_setup()
    senderp = bank_db.query(Bank).get(sender)
    recipientp = bank_db.query(Bank).get(recipient)

    if not auth_client.check_token(senderp.username, token):
        return

    sender_balance = senderp.zoobars - zoobars
    recipient_balance = recipientp.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        raise ValueError()

    senderp.zoobars = sender_balance
    recipientp.zoobars = recipient_balance
    bank_db.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

def balance(username):
    db = bank_setup()
    person = db.query(Bank).get(username)
    return person.zoobars

def register(username):
    db = bank_setup()
    new_zoobar = Bank()
    new_zoobar.username = username
    db.add(new_zoobar)
    db.commit()

def get_log(username):
    db = transfer_setup()
    l = db.query(Transfer).filter(or_(Transfer.sender==username,
                                      Transfer.recipient==username))
    r = []
    for t in l:
       r.append({'time': t.time,
                 'sender': t.sender ,
                 'recipient': t.recipient,
                 'amount': t.amount })
    return r 


