import os, json, sys
OUT = os.path.dirname(os.path.abspath(__file__)); os.environ['EXPC_LED'] = f'{OUT}/expc3-ledger.jsonl'
import exp_c as X
from recall import fill
SUMM = ("Below are excerpts from past conversations between a user and an assistant, with session dates.\n\n{c}\n\n"
        "Write a short free-form prose summary of what these conversations say that is relevant to the question. Plain paragraphs, no tables or lists. No commentary.\n\nQuestion: {q}\nSummary:")
ids = json.load(open(f'{OUT}/exp-c2-ids.json'))['ids']; n = int(sys.argv[1]) if len(sys.argv) > 1 else len(ids)
arms = sys.argv[2].split(',') if len(sys.argv) > 2 else ['bm25_3000', 'summary', 'summary1024', 'state768']
D = {e['question_id']: e for e in json.load(open('data/longmemeval_s.json')) if e['question_id'] in ids}
RF = f'{OUT}/expc3-rows.json'; rows = json.load(open(RF)) if os.path.exists(RF) else []
done = {(r['qid'], r['arm']) for r in rows}
for qid in ids[:n]:
    e = D[qid]; ks, tx, rk = X.turns(e); c1, c3, c768, topk = X.contexts(e)
    sc = X.BM([tx[k].split(': ', 1)[1] for k in ks]).score(e['question']); bm = sorted(range(len(ks)), key=lambda i: -sc[i])
    for arm in arms:
        if (qid, arm) in done: continue
        pre = []
        if arm == 'bm25_3000': ctx = topk
        elif arm == 'bm25_4400': ctx = fill([(tx[ks[i]], set()) for i in bm], 4400)[0]
        elif arm == 'summary':
            s = X.call(SUMM.format(c=topk, q=e['question']), 400, f'{qid}|summ'); pre = [s]
            ctx = 'SUMMARY:\n' + X.trunc(s['text'], 250) + '\n\nRETRIEVED:\n' + c768
        elif arm == 'summary1024':
            s = X.call(SUMM.format(c=topk, q=e['question']), 400, f'{qid}|summ'); pre = [s]
            ctx = 'SUMMARY:\n' + X.trunc(s['text'], 250) + '\n\nRETRIEVED:\n' + c1
        elif arm == 'state768':
            s = X.call(X.STATE.format(c=c768, q=e['question']), 400, f'{qid}|state768'); pre = [s]
            ctx = 'STATE (latest values):\n' + X.trunc(s['text'], 250) + '\n\nRETRIEVED:\n' + c768
        elif arm in ('rand40', 'nodate', 'shuffled'):
            import random, re
            if arm == 'rand40':
                rr = list(range(len(ks))); random.Random(qid).shuffle(rr)
                s = X.call(X.STATE.format(c=fill([(tx[ks[i]][:1500], set()) for i in rr[:40]], 3000)[0], q=e['question']), 400, f'{qid}|staterand'); pre = [s]; blk = X.trunc(s['text'], 250)
            else:
                e2 = e if arm == 'nodate' else D[ids[(ids.index(qid) + 1) % len(ids)]]
                tk2 = X.contexts(e2)[3]; s = X.call(X.STATE.format(c=tk2, q=e2['question']), 400, 'NOCALL'); blk = X.trunc(s['text'], 250)
                if arm == 'nodate': blk = re.sub(r'\[[^\]]*\]\s*', '', blk)
            ctx = 'STATE (latest values):\n' + blk + '\n\nRETRIEVED:\n' + c768
        elif arm == 'full': ctx = '\n'.join(tx[k] for k in ks)
        r = X.call(X.READER.format(c=ctx, d=e['question_date'], q=e['question']), 150, f'{qid}|read|{arm}'); a = r['text']
        votes = [X.call(X.GRADE.format(q=e['question'], g=e['answer'], a=a), 5, f'{qid}|grade3|{arm}|{v}', temp=0.7, seed=v)['text'].lower().startswith('yes') for v in range(3)]
        cs = pre + [r]
        rows.append(dict(qid=qid, arm=arm, ok=sum(votes) >= 2, votes=votes, unknown=a.lower().strip(' .') == 'unknown', gold=str(e['answer'])[:80], answer=a[:300],
                         tok=sum(x['pt'] + x['ct'] for x in cs), usd=sum(x['cost'] for x in cs), ctx_tok=X.count_tokens(ctx)))
        print(qid, arm, int(rows[-1]['ok']), votes, '|', str(e['answer'])[:40], '|', a[:80], flush=True)
        json.dump(rows, open(RF, 'w'), indent=1)
    print('spent', round(X.spent, 4), flush=True)
