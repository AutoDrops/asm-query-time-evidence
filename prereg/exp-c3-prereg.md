# EXP-C3 equal-budget control (POST-HOC, same 57 EXP-C2 ids) — committed before any LLM call, 2026-10-15
Requested by council (Рецензент, Арбитр) after EXP-C2. **Post-hoc: same 57 histories already used in EXP-C2; not a fresh confirmation.**
## Token accounting (free, from cache)
EXP-C2 "tok/q" for state = state-builder pass (input ≈2974 tok = bm25 top-40 turns, each ≤1500 chars, filled to 3000 tok; output ≈266) + reader (≈1144 prompt, of which context ≈944 tok: state block ≈172 + bm25@768) + reader output. Reader-visible context: bm25 1020, state 944, recency 1006 → reader-visible already equal. The gap is the extra LLM pass over 3000 tok of bm25 top-k.
## Arms (reader qwen3-235b-a22b-2507 temp 0, same READER prompt, exp_c.py helpers unchanged)
- A bm25@1024 and S state (EXP-C2 cached answers reused, no new calls).
- B3 bm25@3000: exactly the `topk` text the state builder read (equal to state's total input context).
- B44 bm25@4400: bm25 order filled to 4400 tok (equal to total state tok/q).
- U unstructured summary: same STATE-builder input (topk), free-form prose summary prompt (no entity/attribute/date structure), 400 max tokens, truncated to 250 tok, + bm25@768 — identical layout to S.
- F full_history: all turns in session order (~127k tok/q). Run last; if cap stops it, reported partial, descriptive only.
## Grading: strict = 3-vote LLM judge (same GRADE prompt, temp 0.7 seeds 0-2, qwen) on ALL rows of all arms (S and A strict grades reused from sens-judge-all-rows.json cache).
## Tests: one-sided exact sign test S > each arm, ties dropped, alpha 0.05 (descriptive, post-hoc).
## Decision (Рецензент kill rule)
- "state helps" WITHDRAWN if B44 ≥ 31/57 OR B3 ≥ 31/57 (strict), OR S does not beat U (S ≤ U).
- Otherwise: survives equal-budget control (still post-hoc → needs fresh histories + other-family reader/judge).
## Budget: separate ledger expc3-ledger.jsonl, hard cap $1.00 total auto-stop. Quality check after first 3 histories; stop if broken.

## Amendment 1 (ASM Контроль controls), committed after exactly 1 LLM call (bm25_3000 reader on 5025383b, $0.00026; no other arm touched)
- Added arms: **U1024** = same extra LLM pass over topk with free-form SUMM prompt (no state-table format), block ≤250 tok + bm25@1024. **S768** = STATE prompt built only from the same bm25@768 text, block ≤250 + bm25@768. (bm25_3000 = Контроль (a).)
- Rule: if any of bm25_3000 / U / U1024 / S768 is not worse than S (strict), the win is attributed to compute/extra pass, not ASM state structure. (S768 ≥ S means state helps without extra retrieval — reported separately as positive for structure.)
- Run order under $1: bm25_3000, summary, summary1024, state768, then bm25_4400, then full.
- Extra free regrade: number golds scored on the FINAL number in the answer only; plus 3-vote judge from a non-Qwen family on all rows (cheap, counted in cap).
- Disclosures: multi-session category chosen with gold has_answer labels (headroom.py:22, recall of answer turns) → selection used gold. Known misgrade 6456829e ('5 tomato and 3 cucumber' accepted as 8). The earlier 'strict 34 vs 24' (EXP-C2-SENSITIVITY.md) was uncommitted and used the same Qwen judge → not truly strict/independent.

## Amendment 2 (Gemini + ChatGPT), committed before any call of these arms; cap raised to $2 (parent/user)
- **rand40**: STATE prompt over 40 RANDOM turns (random.Random(qid), each ≤1500 chars, filled to 3000 tok) + bm25@768.
- **nodate**: S's exact cached state block with '[date]' prefixes removed (param=value only) + bm25@768 (reader call only).
- **shuffled**: state block of the NEXT question in id order (wrong question) + bm25@768 → pure-format effect.
- Gemini refutation: if summary or summary1024 is within 3 pts of S (S − U ≤ 3), structure claim fails.
- Blind judge (blind_judge.py, gpt-4o-mini, arm hidden, fixed rules) is the PRIMARY strict grade for all verdicts; report one- and two-sided sign p.
- Audit 33/23→34/24: sole diff = 6456829e (all 3 arms), Qwen judge accepted '5 tomato and 3 cucumber' for gold 8.
