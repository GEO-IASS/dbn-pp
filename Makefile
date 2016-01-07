CC=g++
CCFLAGS=-Wall -ansi -pedantic -std=c++11

OBJ=bin/variable.o bin/domain.o bin/factor.o bin/io.o bin/operations.o bin/inference.o bin/main.o
OBJDEBUG=debug/variable.o debug/domain.o debug/factor.o debug/io.o debug/operations.o debug/inference.o debug/main.o

all: dbn

dbn: $(OBJ)
	$(CC) -o $@ $^

bin/%.o: src/%.cpp include/%.h
	$(CC) $(CCFLAGS) -I include/ -O2 -c -o $@ $<

bin/main.o: src/main.cpp
	$(CC) $(CCFLAGS) -I include/ -O2 -c -o $@ $<

debug: clean dbn-debug
	valgrind --leak-check=full ./dbn-debug data/models/enough-sleep.duai data/models/enough-sleep.evidence

dbn-debug: $(OBJDEBUG)
	$(CC) -o $@ $^

debug/%.o: src/%.cpp include/%.h
	$(CC) $(CCFLAGS) -I include/ -g -c -o $@ $<

debug/main.o: src/main.cpp
	$(CC) $(CCFLAGS) -I include/ -g -c -o $@ $<

.PHONY: clean
clean:
	rm -rfv dbn bin/*.o dbn-debug dbn-debug.dSYM/ debug/*.o
