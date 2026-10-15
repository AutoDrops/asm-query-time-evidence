import json, os, re, random, sys, collections
sys.path.insert(0, '../experiments/exp004'); sys.path.insert(0, '../asm-next-exp003')
from recall import BM, fill
DS = 'data/longmemeval_s.json'
D = json.load(open(DS)); CATS = ['knowledge-update', 'temporal-reasoning', 'multi-session']
ids = {e['question_id'] for e in D}; pat = re.compile(r'[0-9a-f]{8}(?:_abs)?')
used = set()
for root in ['<project-root>/asm-exp004', '../asm-next-exp003', '<project-root>/asm-control', '<project-root>/asm-bench-candidates']:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', 'exp005-headroom')]
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.getsize(p) > 30e6 or 'lme_s' in f or 'longmemeval' in f or 'exp003-heldout' in f or 'f3-head-snapshot' in p: continue
            try: used |= set(pat.findall(open(p, errors='ignore').read())) & ids
            except Exception: pass
c3=json.load(open('<project-root>/asm-exp004/configs/exp003-heldout.json')); used |= (set(c3['excluded_question_ids']) | set(c3['prior_question_ids'])) & ids
json.dump(sorted(used), open('excluded.json', 'w'))
def run(e, B):
    keys, txt, dt = [], {}, {}
    for si, (sid, s, d) in enumerate(zip(e['haystack_session_ids'], e['haystack_sessions'], e['haystack_dates'])):
        for i, t in enumerate(s): k = (si, i); keys.append(k); txt[k] = t; dt[k] = d
    need = [k for k in keys if txt[k].get('has_answer')]
    order = sorted(range(len(e['haystack_dates'])), key=lambda si: (e['haystack_dates'][si], si))
    rk = {si: r / max(1, len(order) - 1) for r, si in enumerate(order)}
    last = max(need, key=lambda k: (rk[k[0]], k[1]))
    sc = BM([txt[k]['content'] for k in keys]).score(e['question'])
    lab = lambda k: (f"[{dt[k]}] {txt[k]['role']}: {txt[k]['content']}", {k})
    bm = sorted(range(len(keys)), key=lambda i: -sc[i])
    cand = [i for i in bm[:40] if sc[i] > 0]; m = max([sc[i] for i in cand] or [1])
    rec = sorted(cand, key=lambda i: -(sc[i] / m + 0.3 * rk[keys[i][0]]))
    out = {}
    for arm, o in (('bm25', bm), ('recency', rec)):
        _, cov = fill([lab(keys[i]) for i in o], B)
        out[arm] = dict(latest=int(last in cov), all=sum(k in cov for k in need) / len(need), full=int(all(k in cov for k in need)))
    return out
res = {}
for c in CATS:
    pool = sorted(e['question_id'] for e in D if e['question_type'] == c and not e['question_id'].endswith('_abs') and e['question_id'] not in used)
    if not pool: res[c] = dict(pool=0); continue
    samp = random.Random(20261015).sample(pool, min(20, len(pool))); E = {e['question_id']: e for e in D}
    r = {q: {B: run(E[q], B) for B in (768, 1024)} for q in pool}
    agg = {f'{a}@{B}': dict(latest=round(sum(r[q][B][a]['latest'] for q in pool) / len(pool), 3), all=round(sum(r[q][B][a]['all'] for q in pool) / len(pool), 3)) for B in (768, 1024) for a in ('bm25', 'recency')}
    res[c] = dict(pool=len(pool), recall=agg, sample=samp,
        miss_latest=sum(1 - r[q][1024]['bm25']['latest'] for q in samp), miss_any=sum(1 - r[q][1024]['bm25']['full'] for q in samp),
        recency_miss_latest=sum(1 - r[q][1024]['recency']['latest'] for q in samp))
json.dump(dict(excluded=len(used), res=res), open('results.json', 'w'), indent=1)
import collections as C; print(len(used), C.Counter(e['question_type'] for e in D if e['question_id'] in used)); [print(c, v.get('pool'), v.get('recall'), v.get('miss_latest'), v.get('miss_any'), v.get('recency_miss_latest')) for c, v in res.items()]
