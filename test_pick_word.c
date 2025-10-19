#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#include "pick_word.h"

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("Usage: %s trie-file\n", argv[0]);
    return 1;
  }
  FILE *romfile = fopen(argv[1], "rb");
  if (romfile == nullptr) {
    printf("%s\n", strerror(errno));
    return 1;
  }
  char buf[20];
  unsigned char *ROM =
      mmap(NULL, 0x4000000, PROT_READ, MAP_PRIVATE, fileno(romfile), 0);
  LEXICON = (Trie *)(ROM);
  if (LEXICON == MAP_FAILED) {
    printf("%s\n", strerror(errno));
    return 1;
  }
  int hist[26] = {0};
  unsigned int unused_factor;
  for (int i = 0; i < 1000000; i++) {
    srand(i);
    mcmc_word(buf, 5);
    // random_word(buf, &unused_factor, 5);
    if (strcmp(buf, "SACQUM") == 0) {
      printf("%d: %s\n", i, buf);
    }
    // printf("%s\n", buf);
    hist[buf[0] - 'A']++;
  }
  for (int c = 0; c < 26; c++) {
    printf("%c %d\n", c + 'A', hist[c]);
  }
  fclose(romfile);
}
