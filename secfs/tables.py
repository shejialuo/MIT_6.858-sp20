# This file contains all code handling the resolution and modification of i
# mappings. This includes group handle indirection and VSL validation, so the
# file is somewhat hairy.
# NOTE: an ihandle is the hash of a principal's itable, which holds that
# principal's mapping from inumbers (the second part of an i) to inode hashes.

import pickle
import secfs.store
import secfs.fs
from secfs.types import I, Principal, User, Group

# a server connection handle is passed to us at mount time by secfs-fuse
server = None
def register(_server):
    global server
    server = _server

def pre(refresh, user):
    """
    Called before all user file system operations, right after we have obtained
    an exclusive server lock.
    """

    # We need to store the `previous_version_structure_list` because
    # we need to compare the `version_structure_list` with the
    # `previous_version_structure_list` to check the consistency.
    import copy
    global version_structure_list, previous_version_structure_list
    previous_version_structure_list = copy.deepcopy(version_structure_list)

    # Download the `version_structure_list` from the server
    version_structure_list.download()
    if refresh != None:
        # refresh usermap and groupmap
        refresh()


def post(push_vs):
    if not push_vs:
        # when creating a root, we should not push a VS (yet)
        # you will probably want to leave this here and
        # put your post() code instead of "pass" below.
        return
    global version_structure_list, previous_version_structure_list

    import os
    current = User(os.getuid())
    version_structure = version_structure_list.version_structures[current]

    # Update the `version_structure` for the current user
    for principal, vs in version_structure_list.version_structures.items():
        if principal != current:
            version_structure.version_vector[principal] = vs.version_number

    # Update itself version number
    version_structure.version_number += 1

    # Update group version number which consists of the current user
    for principal, vs in version_structure_list.version_structures.items():
        if isinstance(principal, Group) and current in vs.version_vector:
            vs.version_number += 1

    # Check the consistency
    ok = True
    for principal, vs in version_structure_list.version_structures.items():
        if principal in previous_version_structure_list.version_structures:
            if previous_version_structure_list.version_structures[principal].version_number > vs.version_number:
                ok = False
                break

    if ok:
        version_structure_list.upload()
    else:
        version_structure_list = previous_version_structure_list

class VersionStructure:
    """
    `VersionStructure` is the most important data structure in this lab. In
    the original SUNDR paper, the version structure is specified only for
    the `User`. Each user could have one and more group handles. However,
    it's a bad idea for the current code. Because the `current_itables`
    mapping the `I` to the inode. The `I.p` could be user or the group.
    """

    version_vector : dict[Principal, int]
    # It could be the user or the group, it is only the hash, should
    # later read from
    i_handle: str

    # current version_number, increasing monotonically
    version_number: int

    def __init__(self):
        self.version_vector = {}
        self.i_handle = ""
        self.version_number = 0

class VersionStructureList:
    """
    `VersionStructureList` is the core data structure here, It
    contains the the user or the group `VersionStructure`.
    """

    version_structures: dict[Principal, VersionStructure]

    def __init__(self) -> None:
        self.version_structures = {}

    def download(self) -> None:
        """
        Download the `version_structure_list` from the server, it should
        be called every time it operates on the file system. It's may
        be a bad idea, but it is simple.
        """

        global server
        blob = server.read_version_structure_list()

        if blob == None:
            return

        if "data" in blob:
            import base64
            blob = base64.b64decode(blob["data"])

        self.version_structures = pickle.loads(blob)

    def upload(self) -> None:

        global server
        blob = pickle.dumps(self.version_structures)
        server.store_version_structure_list(blob)

previous_version_structure_list = VersionStructureList()
version_structure_list = VersionStructureList()

class Itable:
    """
    An itable holds a particular principal's mappings from inumber (the second
    element in an i tuple) to an inode hash for users, and to a user's i for
    groups.
    """
    def __init__(self):
        self.mapping = {}

    def load(ihandle):
        b = secfs.store.block.load(ihandle)
        if b == None:
            return None

        t = Itable()
        t.mapping = pickle.loads(b)
        return t

    def bytes(self):
        return pickle.dumps(self.mapping)

def resolve(i: I, resolve_groups = True):
    """
    Resolve the given i into an inode hash. If resolve_groups is not set, group
    is will only be resolved to their user i, but not further.

    In particular, for some i = (principal, inumber), we first find the itable
    for the principal, and then find the inumber-th element of that table. If
    the principal was a user, we return the value of that element. If not, we
    have a group i, which we resolve again to get the ihash set by the last
    user to write the group i.
    """
    if not isinstance(i, I):
        raise TypeError("{} is not an I, is a {}".format(i, type(i)))

    principal = i.p

    if not isinstance(principal, Principal):
        raise TypeError("{} is not a Principal, is a {}".format(principal, type(principal)))

    if not i.allocated():
        # someone is trying to look up an i that has not yet been allocated
        return None

    global version_structure_list
    if principal not in version_structure_list.version_structures:
        # User does not yet have an itable
        return None

    i_handle = version_structure_list.version_structures[principal].i_handle
    t = Itable.load(i_handle)

    if i.n not in t.mapping:
        raise LookupError("principal {} does not have i {}".format(principal, i))

    # santity checks
    if principal.is_group() and not isinstance(t.mapping[i.n], I):
        raise TypeError("looking up group i, but did not get indirection ihash")
    if principal.is_user() and isinstance(t.mapping[i.n], I):
        raise TypeError("looking up user i, but got indirection ihash")

    if isinstance(t.mapping[i.n], I) and resolve_groups:
        # we're looking up a group i
        # follow the indirection
        return resolve(t.mapping[i.n])

    return t.mapping[i.n]

def modmap(mod_as: User, i: I, ihash) -> I:
    """
    Changes or allocates i so it points to ihash.

    If i.allocated() is false (i.e. the I was created without an i-number), a
    new i-number will be allocated for the principal i.p. This function is
    complicated by the fact that i might be a group i, in which case we need
    to:

      1. Allocate an i as mod_as
      2. Allocate/change the group i to point to the new i above

    modmap returns the mapped i, with i.n filled in if the passed i was no
    allocated.
    """
    if not isinstance(i, I):
        raise TypeError("{} is not an I, is a {}".format(i, type(i)))
    if not isinstance(mod_as, User):
        raise TypeError("{} is not a User, is a {}".format(mod_as, type(mod_as)))

    assert mod_as.is_user() # only real users can mod

    if mod_as != i.p:
        print("trying to mod object for {} through {}".format(i.p, mod_as))
        assert i.p.is_group() # if not for self, then must be for group

        real_i = resolve(i, False)
        if isinstance(real_i, I) and real_i.p == mod_as:
            # We updated the file most recently, so we can just update our i.
            # No need to change the group i at all.
            # This is an optimization.
            i = real_i
        elif isinstance(real_i, I) or real_i == None:
            if isinstance(ihash, I):
                # Caller has done the work for us, so we just need to link up
                # the group entry.
                print("mapping", i, "to", ihash, "which again points to", resolve(ihash))
            else:
                # Allocate a new entry for mod_as, and continue as though ihash
                # was that new i.
                # XXX: kind of unnecessary to send two VS for this
                _ihash = ihash
                ihash = modmap(mod_as, I(mod_as), ihash)
                print("mapping", i, "to", ihash, "which again points to", _ihash)
        else:
            # This is not a group i!
            # User is trying to overwrite something they don't own!
            raise PermissionError("illegal modmap; tried to mod i {0} as {1}".format(i, mod_as))

    # find (or create) the principal's itable
    t = None
    global version_structure_list
    if i.p not in version_structure_list.version_structures:
        if i.allocated():
            # this was unexpected;
            # user did not have an itable, but an inumber was given
            raise ReferenceError("itable not available")
        t = Itable()
        version_structure_list.version_structures[i.p] = VersionStructure()
        print("no current list for principal", i.p, "; creating empty table", t.mapping)
    else:
        i_handle = version_structure_list.version_structures[i.p].i_handle
        t = Itable.load(i_handle)

    # look up (or allocate) the inumber for the i we want to modify
    if not i.allocated():
        inumber = 0
        while inumber in t.mapping:
            inumber += 1
        i.allocate(inumber)
    else:
        if i.n not in t.mapping:
            raise IndexError("invalid inumber")

    # modify the entry, and store back the updated itable
    if i.p.is_group():
        print("mapping", i.n, "for group", i.p, "into", t.mapping)
    t.mapping[i.n] = ihash # for groups, ihash is an i

    i_handle = secfs.store.block.store(t.bytes())
    version_structure_list.version_structures[i.p].i_handle = i_handle

    return i
