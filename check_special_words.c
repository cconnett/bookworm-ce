#include "check_special_words.h"

#ifdef __arm__
#define gba_strcmp ((strcmp_t *)0x0801c1e1)
#define play_sound ((play_sound_t *)0x08016988)
#else
#include <stdio.h>
strcmp_t *gba_strcmp = strcmp;
void play_sound(int id) { printf("Fake playing sound %d.\n", id); }
#endif

static const char *BONE = "BONE\0\0\0";

int check_special_words(char *candidate_word, char *bonus_word) {
  int result = gba_strcmp(candidate_word, bonus_word);
  if (result == 0) {
    return 0;
  }
  const char *b = BONE;
  for (char *i = candidate_word; *i == *b && *i && *b; i++, b++);
  if (*b == 0) {
    play_sound(40);
  }
  return result;
}
