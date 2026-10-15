# EXP-005 headroom check (pre-registered, $0, no LLM)
Date 2026-10-15. Committed before any computation.
- Data: data/longmemeval_s.json (LongMemEval-S, sha256 prefix d6f21ea9d60a0d56).
- Categories: knowledge-update, temporal-reasoning, multi-session. `_abs` (abstention) questions dropped (no answer turns).
- Pool: questions whose question_id string appears in NO text file under <project-root>/asm-exp004, ../asm-next-exp003, <project-root>/asm-control, <project-root>/asm-bench-candidates (dataset files excluded), i.e. not used in c-series/exp003/exp004 (conservative). Excluded list written to excluded.json.
- Tokenizer/BM25: identical to experiments/exp004/recall.py (k1=1.2,b=0.75, count_tokens from asm_lab.personal_facts). Units = raw turns "[date] role: content", greedy fill to budget.
- Labels: benchmark `has_answer` turns. Metrics per budget 768/1024: latest-answer-turn recall (latest by session date, ties by later position) and all-answer-turns recall (fraction).
- Arm R (BM25 + recency rule): candidates = BM25 top-40 turns with score>0; rank by s/max(s) + 0.3*r, r = session date rank in history normalized to [0,1] (latest=1); greedy fill.
- Sample: seed 20261015, random.Random(seed).sample(sorted(pool qids of category), 20).
- Miss (primary) = latest answer turn not in BM25@1024 context. Secondary: any answer turn missing.
- Decision: experiment C is worth running only in a category with >=4 primary misses on its 20; if several, choose the one with most misses (tie: knowledge-update > multi-session > temporal-reasoning). If none, recommend D (publish negative).
- Note: miss counts use gold labels, so these 20 are NOT selected by BM25 weakness; C would use a fresh selection by text only (see exp-c-prereg-draft.md).

## Amendment 1 (before any recall computed)
First run only produced the exclusion list and crashed: configs/exp003-heldout.json lists the 399 *held-out* (unused) ids, so scanning it excluded them. Fix: skip exp003-heldout.json and its .tmp snapshot copy; its `excluded_question_ids`/`prior_question_ids` (c-series) are also in other files? Not guaranteed, so they are added explicitly. If a category pool has <20, use the whole pool (n reported).

## Amendment 2 (after computation, code-only)
Script crashed on empty KU pool (all 75 non-abs KU used before); guard added, no metric logic changed.
