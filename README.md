# Query-time evidence synthesis over BM25 for long-term conversational memory

Code, preregistrations, cached rows and a technical report for a small, preregistered study on
LongMemEval-S (multi-session category, n = 57).

**Finding.** A single cheap LLM pass over the BM25 top-40 turns, conditioned on the question, raises
multi-session accuracy from 22/57 (BM25 only) to 27–30/57 (blind gpt-4o-mini judge) at about $0.0004–0.0005 per question.
Whether the output is a structured `key = value` state table or free-form notes is **not** shown to matter
(state 30 vs notes 27, sign test 6:3, p = 0.25). Giving the reader more raw BM25 context (3000 or 4400 tokens) does not help (21–22/57).

Author: Bohdan Chernyshuk, independent researcher, Ukraine. Report: `report/report.md` (`report/report.pdf`).

## Reproduce the tables (offline, one command)

```sh
./recompute.sh          # writes results/tables.md; Python 3 stdlib only, no network, no API key
```

## Layout

| path | contents |
|---|---|
| `src/` | arm code: `exp_c.py` (bm25 / state / recency arms, reader, preregistered grader), `exp_c3.py` (equal-budget and mechanism controls), `blind_judge.py` (arm-blind non-Qwen judge), `sens_judge_all.py`, `bm25.py` |
| `prereg/` | preregistration files and `COMMITS.md` (full commit hashes + timestamps of the original repository) |
| `data/` | question ids, all answer rows (`*-rows.json`) and per-call cost ledgers (`*-ledger.jsonl`) |
| `scripts/recompute.py` | recomputes every table and the decision rule from `data/` |
| `provenance/` | the original, unmodified scripts, results notes and run logs |
| `report/` | technical report (markdown + PDF) |

## Re-running the experiments (costs money)

Re-running needs the LongMemEval-S file (`longmemeval_s.json`, MIT, https://github.com/xiaowu0162/LongMemEval)
at `LME_S_PATH` and an `OPENROUTER_API_KEY` in the environment. The LLM response cache used in the original runs is not shipped, so a re-run issues new
calls; with temperature 0 and a fixed provider order answers should be close to, but are not guaranteed to be identical to, the cached rows.
`src/` differs from `provenance/original_scripts/` only in import and file paths. Absolute paths in `provenance/` and `prereg/PREREG.md` were replaced by relative or `<project-root>/...` placeholders (no other edits).

## License
MIT (code). LongMemEval data is not redistributed beyond question ids, gold answers and model outputs in the rows files.
