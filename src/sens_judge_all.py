# POST-HOC sensitivity analysis (not part of prereg): grade exact-kind rows of EXP-C2 with the same 3-vote LLM judge
# used for the other rows. Reader answers come only from cache (abort if any reader call would be new).
import os, json, hashlib, sys
os.environ['EXPC_LED'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sens-ledger.jsonl')
import exp_c as X
from math import comb
ids = json.load(open(f'{X.OUT}/exp-c2-ids.json'))['ids']
D = {e['question_id']: e for e in json.load(open(os.environ.get('LME_S_PATH', 'data/longmemeval_s.json'))) if e['question_id'] in ids}
def cached(p, mt, temp=0, seed=0):
    cf = f"{X.CD}/{hashlib.sha256(f'{X.MODEL}|{p}|{mt}|{temp}|{seed}'.encode()).hexdigest()}.json"
    if not os.path.exists(cf): sys.exit('ABORT: uncached reader/state call ' + p[:60])
    return json.load(open(cf))
orig = {(r['qid'], r['arm']): r for r in json.load(open(f'{X.OUT}/expc2-rows.json'))}
out = []
for qid in ids:
    e = D[qid]; kind = X.exact_kind(e['answer'])
    c1, c3, c768, topk = X.contexts(e)
    st = cached(X.STATE.format(c=topk, q=e['question']), 400)
    c2 = 'STATE (latest values):\n' + X.trunc(st['text'], 250) + '\n\nRETRIEVED:\n' + c768
    for arm, ctx in (('bm25', c1), ('state', c2), ('recency', c3)):
        a = cached(X.READER.format(c=ctx, d=e['question_date'], q=e['question']), 150)['text']
        o = orig[(qid, arm)]
        assert a[:160] == o['answer'], (qid, arm)
        if kind:
            votes = [X.call(X.GRADE.format(q=e['question'], g=e['answer'], a=a), 5, f'{qid}|sensgrade|{arm}|{v}', temp=0.7, seed=v)['text'].lower().startswith('yes') for v in range(3)]
            j = sum(votes) >= 2
        else:
            votes, j = o['votes'], o['ok']
        out.append(dict(qid=qid, arm=arm, kind=o['kind'], exact_ok=o['ok'], judge_ok=j, votes=votes, gold=o['gold'], answer=a))
    print(qid, 'spent', round(X.spent, 4), flush=True)
json.dump(out, open(f'{X.OUT}/sens-judge-all-rows.json', 'w'), indent=1)
R = {}
for r in out: R.setdefault(r['qid'], {})[r['arm']] = r
def sign(a, b, k):
    w = sum(1 for v in R.values() if v[a][k] and not v[b][k]); l = sum(1 for v in R.values() if v[b][k] and not v[a][k]); n = w + l
    return w, l, round(sum(comb(n, i) for i in range(w, n + 1)) / 2 ** n if n else 1, 4)
lines = ['# EXP-C2 post-hoc sensitivity: LLM judge (3-vote) on ALL rows (not prereg)', '',
         '| grading | bm25 | state | recency | state>bm25 (w:l, p) | state>recency (w:l, p) |', '|---|---|---|---|---|---|']
for k, name in (('exact_ok', 'prereg (exact containment for number/date/name)'), ('judge_ok', 'judge on all rows')):
    t = {a: sum(v[a][k] for v in R.values()) for a in ('bm25', 'state', 'recency')}
    lines.append(f"| {name} | {t['bm25']}/57 | {t['state']}/57 | {t['recency']}/57 | {sign('state','bm25',k)} | {sign('state','recency',k)} |")
dis = [r for r in out if r['exact_ok'] != r['judge_ok']]
lines += ['', f'Rows where exact and judge disagree: {len(dis)}. Spend ${X.spent:.4f}.', '']
lines += [f"- {r['qid']} {r['arm']} exact={int(r['exact_ok'])} judge={int(r['judge_ok'])} gold={r['gold']!r} ans={r['answer'][:200]!r}" for r in dis]
open(f'{X.OUT}/EXP-C2-SENSITIVITY.md', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines[:8]))
