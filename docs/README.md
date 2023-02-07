# Secure Untrusted Data Repository

## Source Code Reading

### types.py

> In SUNDR, every file is identified by a `<principal, i-number>` pair:
>
> + `principal`: the user or group allowed to write the file.
> + `i-number`: per-principal inode number.

So in `types.py`, the code have defined the base class `Principal`:

```py
class Principal:
    @property
    def id(self):
        return -1
    def is_user(self):
        return False
    def is_group(self):
        return False
```

And the code defines `User` and `Group` class to derive from `Principal`. The code
is easy to understand.

At last the code defines class `I` to represent `<principal, i-number>` pair

### block.py

In SUNDR, all the contents will be indexed by its SHA-1 of the content itself. So
`block.py` provides the basic unit of the file system. The `block.py` uses `server`
handle to talk with the server. It provides two important functions:

+ `store`: store the given blob at the server, and return the content's hash
+ `load`: load the blob with the given content hash from the server

If you understand the internal of Git, it is easy.

### inode.py

`inode.py` defines `Inode` class to represent inode class.

+ For `load` operation, it uses i-handle to use `block.py`'s `load` function
to load the blob, and deserialization the content, update the variables in the
class.
+ For `read` operation, it is easy, iterate the `blocks`.
+ For `bytes`, just serialize the class.

### tree.py

`tree.py` defines the `Directory` class to represent the directory, it accepts
the `<principal, i-number>` pair (`I`) as the parameter. The code uses other code
to get the i-node, and read the contents.

The most tricky part is to add a record in the directory, we should update the memory
part but also the disk part. It is not hard.

### tables.py

`tables.py` define the `Itable` class to represent the itable, it will holding a mapping
from i-number to the inode. And there are many auxiliary functions:

+ `resolve`: this function accepts the `<principal, i-number>` pair. It will resolve it
to the inode.
+ `modmap`: this function aims to change the mapping of the i-table.
