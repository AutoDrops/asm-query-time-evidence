## Table 1a: EXP-C pilot (n=20/20, preregistered grading: exact match for number/date/name, else 3-vote Qwen judge)
| arm | correct | unknown | mean reader ctx tok | mean total tok/q | mean $/q |
|---|---|---|---|---|---|
| bm25 | 7/20 | 11 | 1018 | 1106 | 0.00012 |
| state | 11/20 | 4 | 965 | 4430 | 0.00056 |
| recency | 7/20 | 11 | 1010 | 1091 | 0.00013 |
state vs bm25: W:L 5:1, one-sided p=0.1094, two-sided p=0.2188
state vs recency: W:L 5:1, one-sided p=0.1094, two-sided p=0.2188

## Table 1b: EXP-C2 confirmatory (n=57/57, preregistered grading: exact match for number/date/name, else 3-vote Qwen judge)
| arm | correct | unknown | mean reader ctx tok | mean total tok/q | mean $/q |
|---|---|---|---|---|---|
| bm25 | 23/57 | 20 | 1020 | 1140 | 0.00011 |
| state | 33/57 | 7 | 944 | 4405 | 0.00053 |
| recency | 23/57 | 23 | 1006 | 1110 | 0.00011 |
state vs bm25: W:L 11:1, one-sided p=0.0032, two-sided p=0.0063
state vs recency: W:L 11:1, one-sided p=0.0032, two-sided p=0.0063

## Table 2: EXP-C3 (post-hoc), n=57 EXP-C2 histories. blind = gpt-4o-mini, arm hidden, strict final-value rules, 3-vote majority (PRIMARY). qwen = 3-vote Qwen judge on all rows.
| arm | blind | qwen | state vs arm, blind W:L | p one-sided | p two-sided | reader ctx tok | total tok/q | $/q (reader+extra pass) |
|---|---|---|---|---|---|---|---|---|
| state | 30/57 | 34/57 | – | – | – | 944 | 4405 | 0.00053 |
| bm25 | 22/57 | 24/57 | 9:1 | 0.011 | 0.021 | 1020 | 1140 | 0.00011 |
| recency | 21/57 | 24/57 | 10:1 | 0.006 | 0.012 | 1006 | 1110 | 0.00011 |
| bm25_3000 | 21/57 | 27/57 | 9:0 | 0.002 | 0.004 | 2982 | 2987 | 0.00028 |
| bm25_4400 | 22/57 | 28/57 | 8:0 | 0.004 | 0.008 | 4396 | 4231 | 0.00039 |
| summary | 27/57 | 33/57 | 6:3 | 0.254 | 0.508 | 871 | 4019 | 0.00041 |
| summary1024 | 24/57 | 32/57 | 9:3 | 0.073 | 0.146 | 1127 | 4263 | 0.00043 |
| state768 | 26/57 | 28/57 | 6:2 | 0.145 | 0.289 | 953 | 2336 | 0.00035 |
| rand40 | 20/57 | 21/57 | 10:0 | 0.001 | 0.002 | 965 | 4401 | 0.00055 |
| nodate | 30/57 | 35/57 | 0:0 | 1.000 | 1.000 | 907 | 1032 | 0.00011 |
| shuffled | 18/57 | 18/57 | 12:0 | 0.000 | 0.000 | 944 | 1162 | 0.00011 |
Note: nodate and shuffled reuse cached state blocks, so their $/q excludes the builder pass; full cost of a state pipeline = state row.

## Table 3: final-number rule (number golds only; the last number stated in the answer must equal gold)
| arm | final-number correct | number-gold rows |
|---|---|---|
| state | 24 | 45 |
| bm25 | 16 | 45 |
| recency | 17 | 45 |
| bm25_3000 | 17 | 45 |
| bm25_4400 | 19 | 45 |
| summary | 23 | 45 |
| summary1024 | 18 | 45 |
| state768 | 21 | 45 |
| rand40 | 13 | 45 |
| nodate | 23 | 45 |
| shuffled | 15 | 45 |

## Decision: best control = summary (27); state = 30; diff = 3; one-sided p = 0.254. Rule (state >= best control + 4 and p < 0.05): NOT MET

## Spend (sum of ledger costs, USD)
- expc-ledger.jsonl: $0.0164
- expc2-ledger.jsonl: $0.0436
- sens-ledger.jsonl: $0.0048
- expc3-ledger.jsonl: $0.1425
- blind-ledger.jsonl: $0.0323
