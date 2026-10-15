# EXP-C2 confirmatory prereg (binding) — committed before any LLM call, 2026-10-15
Follows EXP-C (pilot go-signal 11/20 vs 7/20, 5:1). Everything identical to exp-c-prereg-draft.md FINAL + Amendment 1 (grader fix) unless stated.
## Data
- ALL remaining untouched multi-session histories: EXP-C pool 77 (reproduced exactly by script, pilot ids re-derived and asserted) minus the 20 EXP-C pilot ids = **57**. Excludes the 20 EXP-005 headroom-scored and 20 pilot. Ids: exp-c2-ids.json (order = random.Random(20261017) shuffle; order only matters for early stop).
## Arms / reader / grading: unchanged code exp_c.py (only change: env vars EXPC_IDS/EXPC_ROWS/EXPC_LED for file paths; default n = all ids). Arm1 bm25@1024, Arm2 bm25@768+state256 (LLM), Arm3 recency@1024 (no LLM). Reader qwen3-235b-a22b-2507 temp 0; exact match for number/date/name; else 3-vote judge majority.
## Tests (alpha = 0.05, fixed in advance)
- **Primary: one-sided exact sign test, state (arm2) > bm25 (arm1)**, ties dropped. Note: the request said "arm3 vs arm1"; in this repo's frozen numbering the state arm is arm2 (arm3 = recency), so the primary is the state-vs-bm25 comparison as intended.
- Secondary: one-sided sign test state (arm2) > recency (arm3). Also report recency vs bm25 discordant counts (descriptive).
## Decision
- CONFIRMED if primary p < 0.05 AND kill rules not triggered. Kill: arm2 < arm1+3 (scaled: arm2 − arm1 < 3); arm2 not better than arm3; arm2 < arm1; spend > $1. (The pilot rule "≥2 losses" was for n=20; replaced here by the sign test.)
- Otherwise NOT CONFIRMED → close state line, publish negative (D). No reruns, no edits after start.
- If arm3 ≥ arm2: no-LLM recency suffices.
## Quality / budget
- Quality check after first 3 histories; stop if broken (empty/garbled/grading clearly wrong) → failed run, report. Separate ledger expc2-ledger.jsonl, hard cap $1.00 (auto-stop). Est. ~$0.05.
