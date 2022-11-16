from zoodb import *
from debug import *

import pbkdf2
import hashlib
import random

def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput.encode('utf-8')).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db = cred_setup()
    person = db.query(Cred).get(username)
    if not person:
        return None
    if pbkdf2.PBKDF2(password, person.salt).hexread(32) == person.password:
        return newtoken(db, person)
    else:
        return None

def register(username, password):
    cred_db = cred_setup()
    person = cred_db.query(Cred).get(username)
    if person:
        return None

    new_cred = Cred()
    new_cred.username = username
    new_cred.salt = os.urandom(32)
    new_cred.password = pbkdf2.PBKDF2(password, new_cred.salt).hexread(32)

    cred_db.add(new_cred)
    cred_db.commit()

    return newtoken(cred_db, new_cred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False

    
