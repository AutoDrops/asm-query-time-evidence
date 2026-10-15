import json, collections
from math import comb
S = json.load(open('sens-judge-all-rows.json')); C = json.load(open('expc3-rows.json'))
B = {(r['qid'], r['arm']): r for r in json.load(open('blind-rows.json'))} if __import__('os').path.exists('blind-rows.json') else {}
R = collections.defaultdict(dict)
for r in S: R[r['qid']][r['arm']] = dict(q=r['judge_ok'], b=B.get((r['qid'], r['arm']), {}).get('blind'))
for r in C: R[r['qid']][r['arm']] = dict(q=r['ok'], b=B.get((r['qid'], r['arm']), {}).get('blind'))
arms = ['bm25', 'recency', 'state', 'bm25_3000', 'bm25_4400', 'summary', 'summary1024', 'state768', 'rand40', 'nodate', 'shuffled']
tok = collections.defaultdict(list)
for r in C: tok[r['arm']].append(r['ctx_tok'])
def sg(a, k):
    w = sum(1 for v in R.values() if a in v and v['state'][k] and not v[a][k]); l = sum(1 for v in R.values() if a in v and v[a][k] and not v['state'][k]); n = w + l
    p1 = sum(comb(n, i) for i in range(w, n + 1)) / 2 ** n if n else 1; p2 = min(1, 2 * min(p1, sum(comb(n, i) for i in range(0, w + 1)) / 2 ** n)) if n else 1
    return f'{w}:{l} p1={p1:.3f} p2={p2:.3f}'
for k in ('q', 'b'):
    print('judge', k)
    for a in arms:
        rows = [v[a] for v in R.values() if a in v and v[a][k] is not None]
        if rows: print(f"  {a:12s} {sum(x[k] for x in rows)}/{len(rows)} ctx={round(sum(tok[a])/len(tok[a])) if tok[a] else '-'} state-vs: {sg(a,k) if a!='state' else ''}")
