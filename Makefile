CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -g
TARGET = test_pick_word
OBJS = pick_word.o test_pick_word.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

pick_word.o: pick_word.c pick_word.h
	$(CC) $(CFLAGS) -c $<

test_pick_word.o: test_pick_word.c pick_word.h
	$(CC) $(CFLAGS) -lc -c $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
