CC = gcc

# SMC memory bandwidth benchmark with all available CPUs.
CFLAGS = -O2 -fopenmp -DSTREAM_ARRAY_SIZE=100000000

# Single memory bandwidth benchmark using 1 CPU.
# CFLAGS = -O2 -DSTREAM_ARRAY_SIZE=100000000

all: stream

stream: stream.c
	$(CC) $(CFLAGS) stream.c -o stream

install:
	install stream /usr/local/bin

clean:
	rm -f stream *.o

# an example of a more complex build line for the Intel icc compiler
stream.icc: stream.c
	icc -O3 -xCORE-AVX2 -ffreestanding -qopenmp -DSTREAM_ARRAY_SIZE=80000000 -DNTIMES=20 stream.c -o stream.omp.AVX2.80M.20x.icc
