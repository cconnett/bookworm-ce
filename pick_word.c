#include "pick_word.h"

#include <stdbool.h>
#include <stdio.h>

#ifdef __arm__
#define random_int ((prng_func_t *)0x0801bead)
#else
prng_func_t *random_int = rand;
Trie *LEXICON;
#endif

// ⌊int_max_32 / n⌋ for n in [1,26]
static const int RECIPROCAL_INT_MAX[] = {
    2147483647, 1073741823, 715827882, 536870911, 429496729, 357913941,
    306783378,  268435455,  238609294, 214748364, 195225786, 178956970,
    165191049,  153391689,  143165576, 134217727, 126322567, 119304647,
    113025455,  107374182,  102261126, 97612893,  93368854,  89478485,
    85899345,   82595524};

void random_word(char *out_word, unsigned int *out_factor, const int length) {
restart:
  Trie *start_of_level = LEXICON;
  char *word = out_word;
  *out_factor = 1;
  *word = '\0';
  int expanded_length = length;
  Trie *champion;
  for (int level = 0; level < expanded_length; level++) {
    champion = start_of_level;
    int branches = 0;
    int to_skip = 0;

    {
      Trie *point = start_of_level;
      int uncashed = 0;
      bool continuing;
      do {
        if ((level < expanded_length - 1 && point->is_prefix) ||
            (level == expanded_length - 1 && point->is_word)) {
          if (random_int() <= RECIPROCAL_INT_MAX[branches++]) {
            champion = point;
            to_skip += uncashed;
            uncashed = 0;
          }
          uncashed++;
        }
        continuing = point->list_continues;
        if (level == 0) {
          point += 4;
        } else if (level < 4) {
          point += 3;
        } else {
          point++;
        }
      } while (continuing);
    }
    *out_factor *= branches;
    *word++ = (champion->letter_index) + 'A';
    *word = '\0';
    if (champion->letter_index == ('Q' - 'A')) {
      expanded_length += 1;
    }
    if (branches <= 0) {
      goto restart;
    }

    // Advance to start of next level.
    Trie *point = champion;
    if (level == 0) {
      point += 4 + ((Level0Entry *)champion)->jump_lo +
               (((Level0Entry *)champion)->jump_hi << 16);
    } else if (level < 4) {
      point += 3 + ((Level1Entry *)champion)->jump;
    } else {
      // Discard the rest of the current level,
      while (point++->list_continues);

      // and then skip the requisite number of nested sublists.
      int nested_list_depth = to_skip;
      while (nested_list_depth--) {
        do {
          nested_list_depth += point->is_prefix;
        } while (point++->list_continues);
      }
    }
    start_of_level = point;
  }
  if ((out_word[0] == 'R' && out_word[1] == 'A' && out_word[2] == 'P' &&
       out_word[3] == 'E') ||
      (out_word[0] == 'F' && out_word[1] == 'A' && out_word[2] == 'G')) {
    goto restart;
  }
}

void mcmc_word(char *out_word, int length) {
  unsigned int champion_factor;
  random_word(out_word, &champion_factor, length);
  for (int i = 2; i < 12; i++) {
    char challenger[25];
    unsigned int challenger_factor;
    random_word(challenger, &challenger_factor, length);
    // r / int_max_32 < a / (a+b) <=>
    // r(a+b) / int_max_32 < a <=>
    // (r(a+b) >> 31) < a
    unsigned long long r_a_b = random_int();
    r_a_b *= (challenger_factor + champion_factor * i);
    if ((r_a_b >> 31) < challenger_factor) {
      char *dst = out_word;
      char *src = challenger;
      while ((*dst++ = *src++));
      champion_factor = challenger_factor;
    }
  }
}
