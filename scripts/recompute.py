#!/usr/bin/env python3
"""Recompute every table in the report from cached rows in data/. Offline, stdlib only, no API calls."""
import json, os, collections
from math import comb
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
L = lambda f: json.load(open(os.path.join(D, f)))
def sign(w, l):
    n = w + l
    if not n: return 1.0, 1.0
    p1 = sum(comb(n, i) for i in range(w, n + 1)) / 2 ** n
    lo = sum(comb(n, i) for i in range(0, w + 1)) / 2 ** n
    return p1, min(1.0, 2 * min(p1, lo))
def ledger(f): return sum(json.loads(x)['cost'] for x in open(os.path.join(D, f)) if x.strip())
out = []
P = lambda s='': out.append(s)
# ---- Table 1: EXP-C pilot (n=20) and EXP-C2 confirmatory (n=57), preregistered grading
for name, f, ids in (('EXP-C pilot', 'expc-rows.json', 'exp-c-ids.json'), ('EXP-C2 confirmatory', 'expc2-rows.json', 'exp-c2-ids.json')):
    R = L(f); n = len(L(ids)['ids'])
    by = collections.defaultdict(dict)
    for r in R: by[r['qid']][r['arm']] = r
    P(f'## Table 1{"a" if "pilot" in name else "b"}: {name} (n={len(by)}/{n}, preregistered grading: exact match for number/date/name, else 3-vote Qwen judge)')
    P('| arm | correct | unknown | mean reader ctx tok | mean total tok/q | mean $/q |'); P('|---|---|---|---|---|---|')
    for a in ('bm25', 'state', 'recency'):
        rs = [v[a] for v in by.values() if a in v]
        P(f"| {a} | {sum(r['ok'] for r in rs)}/{len(rs)} | {sum(r['unknown'] for r in rs)} | {sum(r['ctx_tok'] for r in rs)/len(rs):.0f} | {sum(r['tok'] for r in rs)/len(rs):.0f} | {sum(r['usd'] for r in rs)/len(rs):.5f} |")
    for a in ('bm25', 'recency'):
        w = sum(1 for v in by.values() if v['state']['ok'] and not v[a]['ok']); l = sum(1 for v in by.values() if v[a]['ok'] and not v['state']['ok'])
        p1, p2 = sign(w, l); P(f'state vs {a}: W:L {w}:{l}, one-sided p={p1:.4f}, two-sided p={p2:.4f}')
    P()
# ---- Table 2: EXP-C3 all arms on the 57 EXP-C2 ids, Qwen judge and blind gpt-4o-mini judge
S = L('sens-judge-all-rows.json'); C = L('expc3-rows.json'); B = {(r['qid'], r['arm']): r for r in L('blind-rows.json')}
C2 = {(r['qid'], r['arm']): r for r in L('expc2-rows.json')}
R = collections.defaultdict(dict); tok = collections.defaultdict(list); usd = collections.defaultdict(list); ctx = collections.defaultdict(list)
for r in S:
    R[r['qid']][r['arm']] = dict(q=r['judge_ok'], b=B[(r['qid'], r['arm'])]['blind'], f=B[(r['qid'], r['arm'])]['finalnum'])
    c = C2[(r['qid'], r['arm'])]; ctx[r['arm']].append(c['ctx_tok']); tok[r['arm']].append(c['tok']); usd[r['arm']].append(c['usd'])
for r in C:
    R[r['qid']][r['arm']] = dict(q=r['ok'], b=B[(r['qid'], r['arm'])]['blind'], f=B[(r['qid'], r['arm'])]['finalnum'])
    ctx[r['arm']].append(r['ctx_tok']); tok[r['arm']].append(r['tok']); usd[r['arm']].append(r['usd'])
arms = ['state', 'bm25', 'recency', 'bm25_3000', 'bm25_4400', 'summary', 'summary1024', 'state768', 'rand40', 'nodate', 'shuffled']
def wl(a, k):
    w = sum(1 for v in R.values() if a in v and v['state'][k] and not v[a][k]); l = sum(1 for v in R.values() if a in v and v[a][k] and not v['state'][k]); return w, l
P(f'## Table 2: EXP-C3 (post-hoc), n={len(R)} EXP-C2 histories. blind = gpt-4o-mini, arm hidden, strict final-value rules, 3-vote majority (PRIMARY). qwen = 3-vote Qwen judge on all rows.')
P('| arm | blind | qwen | state vs arm, blind W:L | p one-sided | p two-sided | reader ctx tok | total tok/q | $/q (reader+extra pass) |'); P('|---|---|---|---|---|---|---|---|---|')
for a in arms:
    rows = [v[a] for v in R.values() if a in v]
    w, l = wl(a, 'b'); p1, p2 = sign(w, l)
    st = ('–', '–', '–') if a == 'state' else (f'{w}:{l}', f'{p1:.3f}', f'{p2:.3f}')
    m = lambda x: sum(x) / len(x) if x else float('nan')
    P(f"| {a} | {sum(x['b'] for x in rows)}/{len(rows)} | {sum(x['q'] for x in rows)}/{len(rows)} | {st[0]} | {st[1]} | {st[2]} | {m(ctx[a]):.0f} | {m(tok[a]):.0f} | {m(usd[a]):.5f} |")
P('Note: nodate and shuffled reuse cached state blocks, so their $/q excludes the builder pass; full cost of a state pipeline = state row.')
P()
# ---- Table 3: final-number rule on number-gold rows
P('## Table 3: final-number rule (number golds only; the last number stated in the answer must equal gold)')
P('| arm | final-number correct | number-gold rows |'); P('|---|---|---|')
for a in arms:
    rows = [v[a] for v in R.values() if a in v and v[a]['f'] is not None]
    P(f"| {a} | {sum(x['f'] for x in rows)} | {len(rows)} |")
P()
# ---- Decision rule of EXP-C3 (amendment 2, prereg f73439d)
ctrl = {a: sum(v[a]['b'] for v in R.values() if a in v) for a in ('bm25_3000', 'bm25_4400', 'summary', 'summary1024', 'state768')}
best = max(ctrl, key=ctrl.get); s = sum(v['state']['b'] for v in R.values()); w, l = wl(best, 'b'); p1, _ = sign(w, l)
P(f'## Decision: best control = {best} ({ctrl[best]}); state = {s}; diff = {s-ctrl[best]}; one-sided p = {p1:.3f}. Rule (state >= best control + 4 and p < 0.05): {"MET" if s-ctrl[best] >= 4 and p1 < .05 else "NOT MET"}')
P()
# ---- Spend
P('## Spend (sum of ledger costs, USD)')
for f in ('expc-ledger.jsonl', 'expc2-ledger.jsonl', 'sens-ledger.jsonl', 'expc3-ledger.jsonl', 'blind-ledger.jsonl'):
    P(f'- {f}: ${ledger(f):.4f}')
print('\n'.join(out))
