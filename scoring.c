#include "scoring.h"

#include <string.h>
static const unsigned char letter_values[] = {
    2, 8, 5,  5, 2, 12, 7, 8,  2,  24, 12, 4,  7, 3,
    3, 6, 24, 3, 3, 3,  5, 16, 14, 24, 10, 24, 0, 0};

#define game_level ((short *)0x03003f10)
#define best_word_score ((int *)0x03002b3c)
#define strlen ((int (*)(char *))0x0801c2a1)
int CalculateScore(candidate_word *cand) {
  int length = strlen(cand->word);
  if (length < 3) {
    return 0;
  }
  int tile_value = 2 * (*game_level + 1);
  for (int i = 0; i < length; i++) {
    tile_value += letter_values[(cand->word[i] - 'A')];
  }
  int length_multiplier = cand->types.diamonds * 10 + cand->types.ices * 7 +
                          cand->types.golds * 4 + cand->types.greens * 2 +
                          length;
  if (cand->types.plains == 0) {
    length_multiplier += cand->tiles - 1;
  }
  return 5 * tile_value * length_multiplier;
}

int BonusScore() {
  // Use global address for candidate word instead of a function parameter. This
  // avoids reloading it as a parameter during assembly monkey-patching.
  candidate_word *cand = (candidate_word *)0x03002a60;
  int length = strlen(cand->word);
  int tile_value = 0;
  for (int i = 0; i < length; i++) {
    tile_value += letter_values[(cand->word[i] - 'A')];
  }
  tile_value += (cand->tiles - 2) * (cand->tiles - 2);
  return (*best_word_score * tile_value / 5 + 99) / 100 * 100;
}
