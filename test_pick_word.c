#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#include "pick_word.h"

int main() {
  FILE *romfile = fopen("new_dict_final.dat", "rb");
  char buf[20];
  unsigned char *ROM =
      mmap(NULL, 0x4000000, PROT_READ, MAP_PRIVATE, fileno(romfile), 0);
  LEXICON = (Trie *)(ROM);
  if (LEXICON == MAP_FAILED) {
    printf("%s\n", strerror(errno));
    return 1;
  }
  int hist[26] = {0};
  for (int i = 0; i < 10000; i++) {
    mcmc_word(buf, 5);
    hist[buf[0] - 'A']++;
  }
  for (int c = 0; c < 26; c++) {
    printf("%c %d\n", c + 'A', hist[c]);
  }
  fclose(romfile);
}
