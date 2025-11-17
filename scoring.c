#include "scoring.h"

#include <string.h>
static const unsigned char letter_values[] = {
    2, 8, 5,  5, 2, 12, 7, 8,  2,  24, 12, 4,  7, 3,
    3, 6, 24, 3, 3, 3,  5, 16, 14, 24, 10, 24, 0, 0};

#define game_level ((short *)0x03003f10)
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
