ASFLAGS := -m64
CFLAGS  := -m64 -g -std=c99 -Wall -Wno-format-overflow -D_GNU_SOURCE -static
LDFLAGS := -m64
LDLIBS  := 
PROGS   := zookfs zookd2

all: $(PROGS)
.PHONY: all

zookd: %: %.o http.o

zookd2 zookfs: %: %.o http2.o

.PHONY: check
check: $(PROGS)
	./check_lab2.py

.PHONY: setup
setup:
	./chroot-setup.sh



.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)


lab%-handin.tar.gz: clean
	tar cf - `find . -type f | grep -v '^\.*$$' | grep -v '/CVS/' | grep -v '/\.svn/' | grep -v '/\.git/' | grep -v 'lab[0-9].*\.tar\.gz' | grep -v '/submit.token$$' | grep -v libz3.so` | gzip > $@

.PHONY: prepare-submit
prepare-submit: lab2-handin.tar.gz

.PHONY: prepare-submit-a
prepare-submit-a: lab2a-handin.tar.gz

.PHONY: prepare-submit-b
prepare-submit-b: lab2b-handin.tar.gz

.PHONY: submit-a
submit-a: lab2a-handin.tar.gz
	./submit.py $<

.PHONY: submit-b
submit-b: lab2b-handin.tar.gz
	./submit.py $<

.PHONY: submit
submit: lab2-handin.tar.gz
	./submit.py $<

.PRECIOUS: lab2-handin.tar.gz
