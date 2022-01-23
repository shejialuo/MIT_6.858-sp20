ASFLAGS := -m64
CFLAGS  := -m64 -g -std=c99 -Wall -Wno-format-overflow -D_GNU_SOURCE -static
LDFLAGS := -m64
LDLIBS  := 
PROGS   := zookd \
           zookd-exstack \
           zookd-nxstack \
           zookd-withssp \
           shellcode.bin run-shellcode

ifeq ($(wildcard /usr/bin/execstack),)
  ifneq ($(wildcard /usr/sbin/execstack),)
    ifeq ($(filter /usr/sbin,$(subst :, ,$(PATH))),)
      PATH := $(PATH):/usr/sbin
    endif
  endif
endif

all: $(PROGS)
.PHONY: all

zookd: %: %.o http.o
zookd-exstack: %-exstack: %.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@ -z execstack
zookd-nxstack: %-nxstack: %.o http.o
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@
zookd-withssp: %: %.o http-withssp.o
run-shellcode: %: %.o

%.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS) -fno-stack-protector

%-withssp.o: %.c
	$(CC) $< -c -o $@ $(CFLAGS)

%.bin: %.o
	objcopy -S -O binary -j .text $< $@



# For staff use only
staff-bin: zookd zookd-exstack zookd-nxstack
	tar cvzf bin.tar.gz $^

.PHONY: check-crash
check-crash: bin.tar.gz shellcode.bin
	./check-bin.sh
	tar xf bin.tar.gz
	./check-crash.sh zookd-exstack ./exploit-2.py

.PHONY: check-exstack
check-exstack: bin.tar.gz shellcode.bin
	./check-bin.sh
	tar xf bin.tar.gz
	./check-attack.sh zookd-exstack ./exploit-4.py

.PHONY: check-libc
check-libc: bin.tar.gz shellcode.bin
	./check-bin.sh
	tar xf bin.tar.gz
	./check-attack.sh zookd-nxstack ./exploit-5.py

.PHONY: check-crash-fixed
check-crash-fixed: clean $(PROGS) shellcode.bin
	./check-crash.sh zookd-exstack ./exploit-2.py

.PHONY: check-exstack-fixed
check-exstack-fixed: clean $(PROGS) shellcode.bin
	./check-attack.sh zookd-exstack ./exploit-4.py

.PHONY: check-libc-fixed
check-libc-fixed: clean $(PROGS) shellcode.bin
	./check-attack.sh zookd-nxstack ./exploit-5.py

.PHONY: check-fixed
check-fixed: check-crash-fixed check-exstack-fixed check-libc-fixed

.PHONY: check-zoobar
check-zoobar:
	./check_zoobar.py

.PHONY: check
check: check-zoobar check-crash check-exstack check-libc


.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)


lab%-handin.tar.gz: clean
	tar cf - `find . -type f | grep -v '^\.*$$' | grep -v '/CVS/' | grep -v '/\.svn/' | grep -v '/\.git/' | grep -v 'lab[0-9].*\.tar\.gz' | grep -v '/submit.token$$' | grep -v libz3.so` | gzip > $@

.PHONY: prepare-submit
prepare-submit: lab1-handin.tar.gz

.PHONY: prepare-submit-a
prepare-submit-a: lab1a-handin.tar.gz

.PHONY: prepare-submit-b
prepare-submit-b: lab1b-handin.tar.gz

.PHONY: submit-a
submit-a: lab1a-handin.tar.gz
	./submit.py $<

.PHONY: submit-b
submit-b: lab1b-handin.tar.gz
	./submit.py $<

.PHONY: submit
submit: lab1-handin.tar.gz
	./submit.py $<

.PRECIOUS: lab1-handin.tar.gz
