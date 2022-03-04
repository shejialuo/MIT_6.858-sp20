ASFLAGS := -m64
CFLAGS  := -m64 -g -std=c99 -Wall -Wno-format-overflow -D_GNU_SOURCE -static
LDFLAGS := -m64
LDLIBS  := 
PROGS   := zookd

all: $(PROGS)
.PHONY: all

zookd: %: %.o http.o


.PHONY: check
check:
	./check_lab3.py


.PHONY: clean
clean:
	rm -f *.o *.pyc *.bin $(PROGS)


lab%-handin.tar.gz: clean
	tar cf - `find . -type f | grep -v '^\.*$$' | grep -v '/CVS/' | grep -v '/\.svn/' | grep -v '/\.git/' | grep -v 'lab[0-9].*\.tar\.gz' | grep -v '/submit.token$$' | grep -v libz3.so` | gzip > $@

.PHONY: prepare-submit
prepare-submit: lab3-handin.tar.gz

.PHONY: prepare-submit-a
prepare-submit-a: lab3a-handin.tar.gz

.PHONY: prepare-submit-b
prepare-submit-b: lab3b-handin.tar.gz

.PHONY: submit-a
submit-a: lab3a-handin.tar.gz
	./submit.py $<

.PHONY: submit-b
submit-b: lab3b-handin.tar.gz
	./submit.py $<

.PHONY: submit
submit: lab3-handin.tar.gz
	./submit.py $<

.PRECIOUS: lab3-handin.tar.gz
