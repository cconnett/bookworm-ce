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

static const int BETA_BINOMIAL_PMF_TABLE[][4] = {
    {2133568291, 13546466, 360511, 8275},
    {1693596349, 404312526, 46561153, 2931063},
    {1361415660, 641378044, 130654915, 13451031},
    {1106831423, 778647122, 227565901, 32530733},
    {909072383, 850776313, 323981109, 59272610},
    {753574460, 880366354, 413204208, 92124217},
    {629948414, 882327746, 492253496, 129438461},
    {530666415, 866586678, 560206356, 169714975},
    {450195750, 839793723, 617248387, 211685841},
    {384416738, 806420890, 664126623, 254327835},
    {330224918, 769476476, 701837012, 296842540},
    {285254929, 730977076, 731448674, 338624763},
    {247686069, 692262905, 754008289, 379229087},
    {216103560, 654210650, 770491317, 418338892},
    {189398336, 617378446, 781780352, 455739497},
    {166693817, 582105393, 788658919, 491295720},
    {147291850, 548580309, 791813740, 524933568},
    {130632373, 516889489, 791841349, 556625525},
    {116263070, 487049989, 789256652, 586378876},
    {103816315, 459032900, 784502033, 614226510},
    {92991527, 432779611, 777956252, 640219735}};

int pick_length(int bonus_words_completed) {
  int roll = random_int();
  int k = bonus_words_completed > 20 ? 20 : bonus_words_completed;
  k = k < 0 ? 0 : k;
  int length;
  for (length = 3; length < 7 && roll >= BETA_BINOMIAL_PMF_TABLE[k][length - 3];
       roll -= BETA_BINOMIAL_PMF_TABLE[k][length++ - 3]);
  //*((int *)0x03002af4) = 1;
  return length;
}

#define bonus_word_scratch ((char *)0x030040ae)
#define bonus_words_completed_g ((short *)0x030040ac)

void pick_bonus_word() {
  int length = pick_length(*bonus_words_completed_g);
  mcmc_word(bonus_word_scratch, length);
  *bonus_words_completed_g += 1;
}

#define string_render_width ((int (*)(char *))0x08018454)
#define render_text ((void (*)(void *, short, short, char *))0x08018870)
#define active_bonus_word ((char *)0x030040bb)
#define active_font ((short *)0x030051dc)
#define tile_selection ((tile **)0x03004018)
#define num_selected_tiles ((int *)0x03004e9c)

void draw_bonus_word() {
  int to_highlight = 0;
  {
    char *bonus = active_bonus_word;
    tile **selected_tile = tile_selection;
    for (; *bonus && selected_tile < tile_selection + *num_selected_tiles;
         bonus++, to_highlight++, selected_tile++) {
      if (*bonus != (*selected_tile)->letter) {
        to_highlight = 0;
        break;
      }
      if (*bonus == 'Q') {
        bonus++;
        to_highlight++;
      }
    }
  }

  *active_font = 8;  // Bonus, highlighted
  int x_pos = 0x34 - string_render_width(active_bonus_word) / 2;
  char buf[2] = {0, 0};
  for (char *bonus = active_bonus_word; *bonus; bonus++) {
    if (!to_highlight--) {
      *active_font = 7;  // Bonus, plain
    }
    buf[0] = *bonus;
    render_text((void *)0x030012bc, x_pos, 0x8e, buf);
    x_pos += string_render_width(buf) + 1;
  }
}
