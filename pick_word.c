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
  Trie *current = LEXICON;
  char *word = out_word;
  *out_factor = 1;
  *word = '\0';
  int expanded_length = length;
  for (int level = 0; level < expanded_length; level++) {
    int branches = 0;
    int to_skip = 0;
    int uncashed = 0;
    Trie *i = current;

    bool continuing;
    do {
      if ((level < expanded_length - 1 && i->is_prefix) ||
          (level == expanded_length - 1 && i->is_word)) {
        if (random_int() <= RECIPROCAL_INT_MAX[branches++]) {
          current = i;
          to_skip += uncashed;
          uncashed = 0;
        }
        uncashed++;
      }
      continuing = i->list_continues;
      if (level == 0) {
        i += 4;
      } else if (level < 4) {
        i += 3;
      } else {
        i++;
      }
    } while (continuing);

    *out_factor *= branches;
    *word++ = (current->letter_index) + 'A';
    *word = '\0';
    if (current->letter_index == ('Q' - 'A')) {
      expanded_length += 1;
    }
    if (branches <= 0) {
      goto restart;
    }

    if (level == 0) {
      current += 4 + ((Level0Entry *)current)->jump_lo +
                 (((Level0Entry *)current)->jump_hi << 16);
    } else if (level < 4) {
      current += 3 + ((Level1Entry *)current)->jump;
    } else {
      int nested_list_depth = to_skip;
      current = i;
      while (nested_list_depth--) {
        do {
          nested_list_depth += current++->is_prefix;
        } while (current->list_continues);
      }
    }
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
