# EXP-C2 confirmatory results (multi-session, n=57 all remaining untouched, prereg commit 634a149)
| arm | correct | unknown | tok/q | $/q |
|---|---|---|---|---|
| 1 bm25@1024 | 23/57 | 20 | 1140 | 0.00011 |
| 2 bm25@768+state256 | 33/57 | 7 | 4405 | 0.00053 |
| 3 recency@1024 (no LLM) | 23/57 | 23 | 1110 | 0.00011 |
Sign tests (one-sided, alpha 0.05, ties dropped): state vs bm25 11:1, p=0.0032 (primary); state vs recency 11:1, p=0.0032; recency vs bm25 3:3 (descriptive).
Verdict per prereg: **CONFIRMED** (p<0.05; +10 ≥ +3; state > recency; no kill). Recency rule adds nothing. Cost 4.8× bm25/question (<10×).
Caveats: 47/57 graded by exact containment (any number token in answer matching gold counts — lenient, same for all arms; seen once in quality check: a recency answer listing $45 then summing to $50). Single model/reader; LongMemEval-S multi-session only. No retries, no provider failures. Spend $0.0436.
