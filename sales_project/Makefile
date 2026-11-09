CC      = gcc
CFLAGS  = -Wall -Wextra -O2 -std=c11 -pthread -D_GNU_SOURCE -Iinclude
LDFLAGS = -pthread

SRCS_COMMON = src/common.c src/logger.c src/data_loader.c src/report.c
OBJS_COMMON = $(SRCS_COMMON:.c=.o)

all: simulator processor

simulator: simulator/simulator.c $(OBJS_COMMON)
	$(CC) $(CFLAGS) -o simulator/simulator $^ $(LDFLAGS)

processor: processor/main.c $(OBJS_COMMON)
	$(CC) $(CFLAGS) -o processor/processor $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f simulator/simulator processor/processor $(OBJS_COMMON)
	rm -rf data reports logs

.PHONY: all clean
