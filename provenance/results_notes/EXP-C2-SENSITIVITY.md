# EXP-C2 post-hoc sensitivity: LLM judge (3-vote) on ALL rows (not prereg)

| grading | bm25 | state | recency | state>bm25 (w:l, p) | state>recency (w:l, p) |
|---|---|---|---|---|---|
| prereg (exact containment for number/date/name) | 23/57 | 33/57 | 23/57 | (11, 1, 0.0032) | (11, 1, 0.0032) |
| judge on all rows | 24/57 | 34/57 | 24/57 | (11, 1, 0.0032) | (11, 1, 0.0032) |

Rows where exact and judge disagree: 3. Spend $0.0048.

- 6456829e bm25 exact=0 judge=1 gold='8' ans='You initially planted 5 tomato plants and 3 cucumber plants.'
- 6456829e state exact=0 judge=1 gold='8' ans='You initially planted 5 tomato plants and 3 cucumber plants.'
- 6456829e recency exact=0 judge=1 gold='8' ans='You initially planted 5 tomato plants and 3 cucumber plants.'
