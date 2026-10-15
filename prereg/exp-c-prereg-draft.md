# EXP-C (EXP-KILL001) prereg — FINAL (binding)
Status: FINAL, committed before any LLM call (2026-10-15). Code: exp_c.py; ids: exp-c-ids.json. Cap $1.00 (auto-stop in code).
## Why / where
EXP-005 headroom (results.json): KU has 0 unused histories; temporal-reasoning BM25@1024 misses 4/20, multi-session 9/20 (latest answer turn). Category: **multi-session** (pre-registered rule: most misses).
## Data / selection (Рецензент 1,5; Арбитр 2)
- 20 FRESH multi-session histories from the EXP-005 unused pool, excluding the 20 EXP-005 sample (those were scored with gold). Pool 97 − 20 = 77.
- Selection by history text only, no gold, no free BM25 pre-run: seed 20261016, random.Random(seed).sample(sorted(pool), 20). Optional "BM25-weak" filter is NOT used; if ever used it must be gold-free, committed, and the report must state the sample is biased toward state and conclusions apply only to such histories.
- Committed (ids + this file) before the run. No reruns, no edits after start.
## Arms (same reader budget 1024 tok)
1. BM25 raw turns @1024.
2. BM25 @768 + 256-tok state block (latest value per entity/attribute, timestamped), 1 cheap LLM pass over BM25 top-k only.
3. BM25 @1024 + recency rule, no LLM (Арбитр 1): candidates BM25 top-40, rank s/max(s) + 0.3·session-date-rank (as EXP-005).
- Reader as EXP-003 (qwen3-235b), temperature 0.
## Grading (Арбитр 5)
- Answers that are a number, date, or name: deterministic normalized exact match vs gold. Otherwise LLM judge 3×, majority.
## Metrics (Рецензент 4)
- Correct count per arm; discordant pairs arm2 vs arm1 and arm2 vs arm3.
- Per arm: 'unknown'/abstain rate, input+output tokens per question, $ per question. If state gives +3 but costs >10× BM25, record it in the conclusion.
## Decision
- GO signal (wording: "pilot go-signal", NOT "significant win"; sign test 4:0 p≈0.125, Арбитр 3 / Рецензент 2): arm2 ≥ arm1+3 AND ≥4 wins with 0–1 losses vs arm1 AND arm2 > arm3.
- KILL if any: arm2 < arm1+3; ≥2 losses vs arm1; arm2 not better than arm3 (recency); arm2 < arm1; spend > $1 (stop immediately).
- Tie = final close of the state line (Рецензент 3): no new variants; publish negative (D).
- If arm3 ≥ arm2, report that the no-LLM recency rule is sufficient and the LLM state block is unnecessary.
## Budget
Est. $0.4–0.8 (reader 60, state 20, judge ≤3× on non-exact items); hard cap $1.00, provider fallback allowed.

## Final values (frozen)
- Pool 77 (multi-session, non-_abs, not in excluded.json, not in EXP-005 sample). Ids = exp-c-ids.json (seed 20261016).
- Arm names in code: bm25 = arm1, state = arm2, recency = arm3.
- State pass: qwen3-235b-a22b-2507, temp 0, input = BM25 top-40 turns (each ≤1500 chars) packed to ≤3000 tok, output ≤400 tok, truncated by lines to ≤250 tok and prepended to BM25@768.
- Reader: same model, temp 0, max 150 tok, EXP-004 prompt. Provider DeepInfra preferred, fallback allowed (logged).
- Grading: gold number/date/name (regex in exp_c.exact_kind) → normalized exact containment (numbers also as words 0–20); else LLM judge (same model, LongMemEval multi-session prompt) 3 votes, temp 0.7 seeds 0–2, majority.
- Quality check after first 3 histories; stop if outputs broken (empty/garbled/grading clearly wrong) and report as failed run, no reruns with changes.

## Amendment 1 (after quality check on first 3 histories, before the rest)
- Grader bug: trailing sentence period kept in tokens ('$25,000.' ≠ '25000'), so a correct recency answer scored 0. Fix: strip leading/trailing '.' in norm(). Deterministic, arm-independent; reader/state outputs unchanged (cached). Disclosed in report.
- Crash fix: int gold → str(g) in exact(). No grading change.
