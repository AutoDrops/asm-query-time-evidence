# EXP-C3 results (POST-HOC mechanism analysis, same 57 EXP-C2 ids)
Primary grade: blind non-Qwen judge (gpt-4o-mini, arm hidden, strict final-value rules, 3 votes). Full table: c3-report.txt.
| arm | blind | qwen-judge | ctx tok | state vs arm (blind) W:L, p1/p2 |
|---|---|---|---|---|
| state | 30 | 34 | ~944 | – |
| bm25@1024 | 22 | 24 | ~1020 | 9:1, .011/.021 |
| bm25@3000 | 21 | 27 | 2982 | 9:0, .002/.004 |
| bm25@4400 | 22 | 28 | 4396 | 8:0, .004/.008 |
| summary (free-form, same extra pass) | 27 | 33 | 871 | 6:3, .254/.508 |
| summary1024 | 24 | 32 | 1127 | 9:3, .073/.146 |
| state768 (no extra retrieval) | 26 | 28 | 953 | 6:2, .145/.289 |
| rand40 (pass over random turns) | 20 | 21 | 965 | 10:0, .001/.002 |
| nodate | 30 | 35 | 907 | 0:0 |
| shuffled (other question's state) | 18 | 18 | 944 | 12:0, .000/.000 |
## Verdict
Rule: state ≥ best control +4 and p<0.05. Best control = free-form summary 27 → state +3, p1=0.25. **Not met → "structured state helps" NOT supported.**
Thesis: **a cheap query-time LLM pass over BM25 top-40 lifts multi-session** (bm25 22 → summary 27 / state 30 of 57). More raw context does NOT help (bm25@3000/4400 = 21/22). Pass must be query-relevant (rand40 20, shuffled 18). Dates in block irrelevant (nodate = state).
## 33/23 → 34/24 audit
Sole difference = 6456829e (gold 8): Qwen judge accepted "5 tomato and 3 cucumber plants" in all 3 arms (+1 each). Blind judge and final-number rule reject it. Old "strict" file was uncommitted and same-family judge.
## Spend: reader arms $0.1425 + blind judge $0.0323 → total EXP-C3 $0.175.
