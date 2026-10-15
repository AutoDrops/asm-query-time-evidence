# ASM: fact-extraction line on LongMemEval KU — CLOSED (negative result)
Date: 2026-10-15 (Kyiv). Sources: asm-next-exp003/runs/exp003-check1/RESULTS.md, runs/exp003-pilot/rows.jsonl + run.log, experiments/exp004/RESULTS.md, postmortems in asm-control/.

## Result
Fact extraction (EXP-003: key=value personal facts + token-overlap ranker) does not beat plain BM25 over raw turns. No variant tried beats BM25.

| run | n | bm25 | full_history | exp003 / fact variants | spend |
|---|---|---|---|---|---|
| check1 (prereg PASS rule) | 3 | 2/3 | 3/3 | 2/3 | $0.291 |
| pilot (stopped by user after 5 of 30) | 5 | 5/5 | 3/5 | 2/4 (1 row missing) | $0.407 |
| EXP-004 offline retrieval fix, @1024 tok (dev, reused data) | 7 | 7/7 (d) | — | a old 4/7, b fixed facts 3/7, c facts→raw turns 7/7 | $0.0037 |

EXP-004 recall @512 tok: a 6, b 7, c 7, d 7 of 7; recall_all@1024: a 4.67, b 4.17, c 4.17, d 7.0. Variant c only ties BM25 (it is BM25 with an extra costly layer).

## Why (postmortem consensus)
- Ranking: unweighted token overlap; 60–76% of 700–1300 facts/history are assistant_said paraphrases that crowd out user facts. Needed facts ranked ~138–537; BM25 ranks the needed raw turn #1 in 6/7.
- Extraction loses relations (class↔Friday, "half of 10"→5, "3 months" missing).
- Cost: ~50 LLM calls/history for extraction.
- Process: BM25 was never set as the bar to beat before paying; a known retrieval defect was frozen into the pilot.

## Caveats
Tiny n; EXP-004 used already-seen dev histories → diagnostic, not publishable. Frozen v4.4D untouched.

## Decision
Close the fact-extraction line on LongMemEval KU. Any future ASM claim must beat BM25 on fresh histories under a pre-registered rule.
