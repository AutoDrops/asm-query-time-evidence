# EXP-C results (multi-session, n=20, seed 20261016)
| arm | correct | unknown | tok/q | $/q |
|---|---|---|---|---|
| 1 bm25@1024 | 7/20 | 11 | 1106 | 0.00012 |
| 2 bm25@768+state256 | 11/20 | 4 | 4430 | 0.00056 |
| 3 recency@1024 (no LLM) | 7/20 | 11 | 1091 | 0.00013 |
Discordant: state vs bm25 5:1; state vs recency 5:1; recency vs bm25 0:0.
Verdict per prereg: all GO conditions met (11 ≥ 7+3; 5 wins/1 loss; state > recency) → **pilot go-signal, NOT significant** (sign test 5:1, p≈0.22 two-sided). No kill rule triggered. Cost 4.6× bm25 per question (<10×). Recency rule adds nothing here.
Caveats: amendment 1 (exact-match trailing-period fix, after 3 histories) + int-gold crash fix; 17/20 graded by exact match; state gains mostly from fewer 'unknown' on count/aggregation questions. Spend $0.0164.
