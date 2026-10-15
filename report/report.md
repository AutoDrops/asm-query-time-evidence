---
title: "Query-time evidence synthesis over BM25 for long-term conversational memory: a small preregistered study on LongMemEval-S multi-session questions"
author: "Bohdan Chernyshuk (independent researcher, Ukraine)"
date: "October 2026 (technical report, preprint)"
geometry: margin=2.2cm
fontsize: 10pt
---

# Abstract

We test cheap memory pipelines for long chat histories on the multi-session category of LongMemEval-S
(57 unseen histories, ~115k tokens each). The baseline sends the BM25 top turns (1024 tokens) to the reader.
Adding one LLM pass that reads the BM25 top-40 turns (~3000 tokens), conditioned on the question, and writes a short
evidence block raises accuracy from 22/57 to 27–30/57 under a blind, non-Qwen judge. The pass costs about $0.0003–0.0004
per question, roughly 4–5× the baseline in total. A preregistered confirmatory test of the structured
variant against BM25 succeeded (33 vs 23, sign test 11:1, p = 0.003, preregistered grader). Post-hoc controls then
showed that the *structure* of the block is not what matters. A structured `key = value` state table beats free-form
prose notes by only 3 (30 vs 27, 6:3, p = 0.25), and dropping dates from the table changes nothing.
More raw BM25 context does not help: 3000 tokens scores 21/57 and 4400 tokens 22/57. The pass must be query-relevant.
Over random turns it scores 20/57, and with another question's block 18/57. We report all
negative results of the wider project, including an earlier structured-memory system that lost to full history (49 vs 66 of 100) and to BM25.

# 1. Motivation and question

This work grew out of an agent-memory project (ASM). Its earlier version extracted typed facts
ahead of time and lost to simple baselines (Section 7). That pointed to a question: is it better to synthesize evidence at
**query time** over a cheap lexical retrieval than to keep a precomputed fact store? And if a synthesis pass helps, does a
"latest value per attribute" state format help beyond generic summarisation?

# 2. Setup

**Data.** LongMemEval-S (Wu et al., 2024; MIT). We use only the multi-session category and drop abstention questions.
Questions whose id appeared anywhere in our earlier project files were excluded, which gave a pool of 77 multi-session questions. Of these, 20 were
used for a pilot (EXP-C) and the remaining **57** form the confirmatory set (EXP-C2) and the post-hoc control set (EXP-C3).

**Retrieval units.** Raw turns formatted as `[session date] role: content`. BM25 (k1 = 1.2, b = 0.75, stop-word
filter) is computed over each history separately. Contexts are filled greedily to a token budget, where 1 token ≈ 4 characters.

**Reader.** `qwen/qwen3-235b-a22b-2507` via OpenRouter (provider DeepInfra), temperature 0, 150 output tokens, one fixed prompt
("answer concisely using only this memory, else `unknown`").

**Arms** (reader context ≈ 1000 tokens unless stated):

| arm | reader context | extra LLM pass |
|---|---|---|
| bm25 | BM25 @1024 | none |
| recency | BM25 top-40 re-ranked by score + 0.3·session-recency, @1024 | none |
| **state** | state block (≤250 tok) + BM25 @768 | STATE prompt over BM25 top-40 (≤3000 tok) + question → `[date] entity / attribute = latest value`, ≤15 lines |
| bm25_3000 | exactly the 3000-token text the state pass reads | none |
| bm25_4400 | BM25 @4400 (≈ total state tokens per question) | none |
| summary | prose summary (≤250 tok) + BM25 @768 | same input as state, free-form prose prompt (no tables or lists) |
| summary1024 | prose summary + BM25 @1024 | as summary |
| state768 | state block + BM25 @768 | STATE prompt over the same BM25 @768 text only |
| rand40 | state block + BM25 @768 | STATE prompt over 40 *random* turns |
| nodate | state block with dates stripped + BM25 @768 | reused from state |
| shuffled | *another question's* state block + BM25 @768 | reused |

**Grading.** *Preregistered (EXP-C/C2):* exact match for number, date and name golds (any number token in the answer matching the gold counts).
Other golds go to a 3-vote LLM judge (the reader model, LongMemEval-style prompt, temperature 0.7). *Primary for EXP-C3 (fixed before any judge call, commit 03ca6ce):* an
**arm-blind** `openai/gpt-4o-mini` judge with strict rules. The final stated value must equal the reference, lists must be complete, and
hedges or `unknown` count as wrong. It takes a 3-vote majority. Each (question, answer) pair is graded alone, in shuffled order, with no arm identity in the prompt or the cache key.
We also report a free "final number" rule for numeric golds.

**Statistics.** Exact sign test on discordant pairs, ties dropped, both one- and two-sided.

**Preregistration.** Each experiment's design, ids, decision rule and code were committed to git before its first LLM call.
`prereg/COMMITS.md` lists full hashes and timestamps: EXP-C2 at 634a149 (15:59:49 UTC+3, first LLM call 15:59:58),
EXP-C3 at 5a27f56, with amendments b7dede2, 03ca6ce and f73439d.

# 3. Results

## 3.1 Pilot and confirmatory test (preregistered)

| | bm25@1024 | state | recency | state vs bm25 (W:L, p one-sided) | $/q bm25 → state |
|---|---|---|---|---|---|
| EXP-C pilot, n = 20 | 7 | 11 | 7 | 5:1, p = 0.11 | 0.00012 → 0.00056 |
| EXP-C2 confirmatory, n = 57 | 23 | **33** | 23 | **11:1, p = 0.0032** | 0.00011 → 0.00053 |

The preregistered verdict for EXP-C2 was CONFIRMED. The recency re-ranking added nothing (23 = 23).

## 3.2 Equal-budget and mechanism controls (post-hoc, same 57 histories)

EXP-C2 left one competing explanation open: the state arm used ~4405 tokens per question against ~1140 for BM25.
Its reader-visible context was the same size (944 vs 1020 tokens), so the gap came entirely from the extra pass over the top 3000 tokens of BM25.
All arms were then re-graded by the blind judge.

| arm | blind | qwen judge | state vs arm, blind W:L | p (1-s / 2-s) | total tok/q | $/q |
|---|---|---|---|---|---|---|
| **state** | **30** | 34 | – | – | 4405 | 0.00053 |
| bm25@1024 | 22 | 24 | 9:1 | .011 / .021 | 1140 | 0.00011 |
| recency | 21 | 24 | 10:1 | .006 / .012 | 1110 | 0.00011 |
| bm25@3000 | 21 | 27 | 9:0 | .002 / .004 | 2987 | 0.00028 |
| bm25@4400 | 22 | 28 | 8:0 | .004 / .008 | 4231 | 0.00039 |
| **summary (prose)** | **27** | 33 | 6:3 | .254 / .508 | 4019 | 0.00041 |
| summary1024 | 24 | 32 | 9:3 | .073 / .146 | 4263 | 0.00043 |
| state768 | 26 | 28 | 6:2 | .145 / .289 | 2336 | 0.00035 |
| rand40 | 20 | 21 | 10:0 | .001 / .002 | 4401 | 0.00055 |
| nodate | 30 | 35 | 0:0 | – | (reuses state) | |
| shuffled | 18 | 18 | 12:0 | <.001 | (reuses state) | |

Under the final-number rule (45 numeric golds): state 24, summary 23, nodate 23, state768 21, bm25@4400 19, bm25@3000 17, bm25 16, rand40 13.

**Preregistered decision (amendment 2):** the structure claim required state ≥ best control + 4 and p < 0.05. The best control was the
prose summary at 27, so the difference is +3 with p = 0.25. **Not met.** The claim that "structured state helps" is not supported.

## 3.3 Interpretation

1. *Synthesis, not volume.* Handing the reader the same 3000 tokens, or 4400, does not help, while a 250-token synthesis of the same
   text does. Most wins over BM25 are on counting and aggregation questions, where the pass assembles scattered mentions and the BM25-only reader answers `unknown` (unknowns: 20 for bm25 vs 7 for state in EXP-C2).
2. *Query conditioning is necessary.* The same pass over random turns (20) or another question's block (18) is at or below baseline.
   So the gain is not a formatting artefact.
3. *Format is secondary.* Structured vs prose differ by 3/57. Dates inside the block are irrelevant (nodate = state). A state built only from
   the 768 tokens the reader already sees gives 26, which suggests both more input to the pass and the pass itself contribute. Our n cannot separate them.

# 4. Cost

At OpenRouter prices in October 2026, per question: BM25 reader ≈ $0.00011; state or summary pipeline ≈ $0.0004–0.0005,
about 4–5× the baseline but still under $0.03 per 57 questions. Total spend for everything in this report: pilot $0.016, EXP-C2
$0.044, EXP-C2 sensitivity regrade $0.005, EXP-C3 readers $0.143, blind judge $0.032, **≈ $0.24**. A full-history reader on
LongMemEval-S costs around $0.01 per question (~115k tokens).

# 5. Disclosures and threats to validity

- **Post-hoc controls on reused data.** EXP-C3 reused the same 57 histories as EXP-C2, after its result was known.
  Its controls were preregistered before their own calls, but it is not a fresh confirmation. The headline gain of synthesis over BM25 has therefore been confirmed once (EXP-C2) under the preregistered
  grader. Under the blind judge it holds on the same data (state 9:1, p = 0.02 two-sided), but this is post-hoc.
- **Category selection used gold labels.** Multi-session was chosen by a preregistered headroom analysis that measured BM25
  recall of the benchmark's `has_answer` turns (`provenance/original_scripts/headroom.py`, line 22). The knowledge-update category,
  which the project originally targeted, had no unseen questions left: an earlier pilot had hit a ceiling there, with BM25 at 7/7 on a dev subset.
  The result therefore applies to multi-session only.
- **Same-family reader and judge.** The reader is Qwen3-235B, and so is the preregistered EXP-C/C2 judge. The Qwen judge is systematically
  more lenient (up to +8 per arm over the blind judge). It accepted "5 tomato and 3 cucumber plants" for gold 8 in all three
  EXP-C2 arms, which explains a 33/23 → 34/24 discrepancy in an earlier, uncommitted "strict" regrade. Only the judge was changed to a different family.
  **No second reader family was tested.**
- **Lenient preregistered numeric rule.** In EXP-C/C2, any number in the answer matching the gold counted, and this favours longer answers. The blind judge
  and the final-number rule remove this effect, and state stays ahead of BM25 under both.
- **Amendments.** EXP-C had one grader fix after 3 histories (trailing period in exact match) plus a crash fix for integer golds.
  EXP-C3 amendment 1 was committed after exactly one reader call (bm25@3000 on one question). `blind_judge.py` was parallelised
  in the results commit (thread pool only; prompt, rules, seeds and order unchanged).
- **Not run.** A full-history arm and dense or hybrid retrievers at equal budget were planned but not run. Other LongMemEval categories, LongMemEval-M and
  LoCoMo are not covered.
- **Small n.** With 57 questions, differences of ±3 are not resolvable.
- **Authorship.** Experiments were designed and run with heavy use of LLM-based assistants, and reviewed by LLM-based "council" agents
  rather than independent humans.

# 6. What we claim

On LongMemEval-S multi-session, one cheap query-conditioned LLM pass over BM25 top-40 raw turns improves a fixed reader
from 22 to 27–30 of 57 under a blind cross-family judge. Simply giving the reader more retrieved text does not.
We do **not** claim that a structured state format beats free-form notes, that the effect transfers to other categories, readers or
benchmarks, or that it beats a full-context reader.

# 7. Negative results from the wider project

- **LongMemEval oracle subset, earlier ASM system (frozen v4.2), EXP-002-oracle, 10 Oct 2026 (preregistered; analysis commit bf711f9).** On a 100-question stratified subset of LongMemEval *oracle* (cleaned; seed 2002; not the 500-question benchmark, not LongMemEval-S), a precomputed structured memory scored **49/100 vs 66/100 for full history** (BM25 58, LLM summary 49). ASM − BM25 = −9 pp, 95% CI [−17, −1], McNemar p = 0.064; ASM − full history = −17 pp, p = 0.0015. On multi-session: ASM 6/27 vs full history 17/27. Answer-bearing turns reached the ASM context in 41% of cases (BM25 78%).
- **LoCoMo (dev conversation conv-26, 10 questions).** ASM v4.4D scored **0/10** against ~7/10 for full history. The frozen extractor stored no ordinary
  facts: of 191 items, 110 were quotes, 46 were intents and 0 were assertions. The main LoCoMo run was not launched.
- **EXP-003 / EXP-004, fact extraction on LongMemEval knowledge-update.** Key=value personal-fact extraction with a token-overlap ranker
  did not beat plain BM25 over raw turns. It scored 2/3 vs bm25 2/3 and full history 3/3 in a preregistered check, and 2/4 vs 5/5 in a pilot stopped early. In an offline retrieval
  fix with n = 7, fact variants scored 3–4/7, and mapping facts back to raw turns only tied BM25 (7/7). Extraction needed ~50 LLM calls per history,
  and 60–76% of facts were paraphrases of assistant turns. The line was closed.
- Across these, BM25 over raw turns was a strong baseline that precomputed fact memories failed to beat. This motivated moving synthesis to
  query time.

# 8. Next steps

Confirm on fresh histories (temporal-reasoning, LongMemEval-M) with a second, non-Qwen reader and judge, and add full-history and dense or hybrid
arms at equal budget, all under a new preregistration.

# Reproducibility

Code, preregistrations with commit hashes, every answer row and per-call cost ledgers are in this repository. `./recompute.sh`
regenerates every table in Sections 3–4 offline from the cached rows.

# References

- D. Wu et al. *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory.* arXiv:2410.10813, 2024.
- A. Maharana et al. *Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo).* arXiv:2402.17753, 2024.
- S. Robertson, H. Zaragoza. *The Probabilistic Relevance Framework: BM25 and Beyond.* 2009.
