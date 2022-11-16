# Lab 2

When starting `zookld.py`, the container produces following errors:

```txt
The repository 'http://security.ubuntu.com/ubuntu impish-security Release' no longer has a Release file
```
When reading the source code, I have find the shell scripts `download.sh` in
`/usr/local/6858/lxcbase`. Thus, I decide to change the shell script to make it
download the latest image.

## Part 1

It's easy.

## Part 2

The first job is to split the monolithic applications to microservices. It is easy.
We first need to ensure the interfaces.

+ `auth.login`
+ `auth.register`
+ `auth.check_token`

So we need to update the `auth-server.py` to call these functions. Next, we need to
update the `auth_client.py` to support these RPC calls. And last we should change the
`login.py` to call `auth_client.py` method.

Well, the tricky part is for the database.

And next we hash the password with salt.

## Part 3

Just like part 2, However, do remember each database is independent. And we need to
ensure the secuirty to transfering the money. Easy job.
