#ifndef _PICK_WORD_H
#define _PICK_WORD_H

typedef int prng_func_t(void);
extern prng_func_t *random_int;
#ifndef __arm__
#include <stdlib.h>
#endif

typedef struct __attribute__((packed)) {
  unsigned int letter_index : 5;
  unsigned int is_word : 1;
  unsigned int is_prefix : 1;
  unsigned int list_continues : 1;
} Trie;

typedef struct __attribute__((packed)) {
  Trie t;
  unsigned short jump_lo;
  unsigned char jump_hi;
} Level0Entry;

typedef struct __attribute__((packed)) {
  Trie t;
  unsigned short jump;
} Level1Entry;

#ifdef __arm__
#define LEXICON ((Trie *)0x080f7c38)
#else
extern Trie *LEXICON;
#endif

// ⌊int_max_32 / n⌋ for n in [1,26]
static const int RECIPROCAL_INT_MAX[27];
void random_word(char *out_word, unsigned int *out_factor, int length);
void mcmc_word(char *out_word, int length);

#endif
