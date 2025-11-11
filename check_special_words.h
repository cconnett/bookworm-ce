#ifndef _CHECK_SPECIAL_WORDS_H
#define _CHECK_SPECIAL_WORDS_H

typedef int strcmp_t(char *, char *);
typedef void play_sound_t(int);
extern strcmp_t *gba_strcmp;

int check_special_words(char *candidate_word, char *bonus_word);

#endif
