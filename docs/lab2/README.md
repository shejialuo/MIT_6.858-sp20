# Lab 2

When starting `zookld.py`, the container produces following errors:

```txt
The repository 'http://security.ubuntu.com/ubuntu impish-security Release' no longer has a Release file
```
When reading the source code, I have find the shell scripts `download.sh` in
`/usr/local/6858/lxcbase`. Thus, I decide to change the shell script to make it
download the latest image.
