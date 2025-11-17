#ifndef _SCORING_H
#define _SCORING_H

typedef struct {
  unsigned char plains;
  unsigned char greens;
  unsigned char golds;
  unsigned char fires;
  unsigned char ices;
  unsigned char diamonds;
} type_count;

typedef struct {
  char word[26];
  type_count types;
  int tiles;
  int score;
} candidate_word;

int CalculateScore(candidate_word *cand);

#endif
