import json, os, re, sys, time, hashlib, urllib.request, collections
sys.path.insert(0, '../experiments/exp004'); sys.path.insert(0, '../asm-next-exp003')
from recall import BM, fill
from asm_lab.personal_facts import count_tokens
OUT = os.path.dirname(os.path.abspath(__file__)); CD = f'{OUT}/expc-cache'; os.makedirs(CD, exist_ok=True)
MODEL = 'qwen/qwen3-235b-a22b-2507'; CAP = 1.0; LED = os.environ.get('EXPC_LED', f'{OUT}/expc-ledger.jsonl')
READER = ("Below is memory retrieved from past conversations between a user and an assistant.\n\n{c}\n\n"
          "Answer the question concisely using only this memory. If it is not answerable, reply exactly: unknown\n\n"
          "Question: (Current date: {d}) {q}\nAnswer:")
STATE = ("Below are excerpts from past conversations between a user and an assistant, with session dates.\n\n{c}\n\n"
         "Write a compact state table of facts about the USER relevant to the question: one line per entity/attribute, "
         "format '[date] entity / attribute = latest value', keep only the most recent value per attribute, include counts/lists if relevant. "
         "Max 15 lines. No commentary.\n\nQuestion: {q}\nState:")
GRADE = ("I will give you a question, a correct answer, and a response from a model. Please answer yes if the response contains the correct answer. Otherwise, answer no. If the response is equivalent to the correct answer or contains all the intermediate steps to get the correct answer, you should also answer yes. If the response only contains a subset of the information required by the answer, answer no.\n\nQuestion: {q}\n\nCorrect Answer: {g}\n\nModel Response: {a}\n\nIs the model response correct? Answer yes or no only.")
spent = sum(json.loads(l)['cost'] for l in open(LED)) if os.path.exists(LED) else 0.
def call(p, mt, tag, temp=0, seed=0):
    global spent
    cf = f"{CD}/{hashlib.sha256(f'{MODEL}|{p}|{mt}|{temp}|{seed}'.encode()).hexdigest()}.json"
    if os.path.exists(cf): return json.load(open(cf))
    if spent >= CAP: sys.exit('CAP $1 reached')
    body = dict(model=MODEL, messages=[{'role': 'user', 'content': p}], max_tokens=mt, temperature=temp, seed=seed, usage={'include': True},
                provider={'order': ['DeepInfra'], 'allow_fallbacks': True})
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', json.dumps(body).encode(),
                {'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'}), timeout=90))
            if 'choices' in r: break
        except Exception as e: print('retry', a, e, flush=True); time.sleep(5)
    else: sys.exit('network')
    u = r.get('usage', {}); c = float(u.get('cost') or 0); spent += c
    res = dict(text=(r['choices'][0]['message'].get('content') or '').strip(), cost=c, pt=u.get('prompt_tokens', 0), ct=u.get('completion_tokens', 0), provider=r.get('provider'))
    open(LED, 'a').write(json.dumps(dict(tag=tag, cost=c, provider=r.get('provider'), spent=spent)) + '\n')
    json.dump(res, open(cf, 'w')); return res
NUMW = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split()
def norm(s): return [w.strip('.') for w in re.sub(r'[^a-z0-9.$% ]', ' ', s.lower().replace(',', '')).split() if w.strip('.')]
def exact_kind(g):
    g = str(g).strip()
    if re.fullmatch(r'\$?[0-9][0-9,.]*%?( [a-z]+){0,2}', g.lower()) or g.lower() in NUMW: return 'number'
    if re.fullmatch(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Z][a-z]+ \d{1,2}(st|nd|rd|th)?(,? \d{4})?|\d{1,2}(st|nd|rd|th)? [A-Z][a-z]+( \d{4})?)', g): return 'date'
    if len(g.split()) <= 3 and all(w[:1].isupper() for w in g.split()) and not re.search(r'\d', g): return 'name'
def exact(g, a):
    g = str(g)
    k = exact_kind(g); A = norm(a)
    if k == 'number':
        n = norm(g)[0].lstrip('$').rstrip('%'); alts = {n, n.rstrip('0').rstrip('.') if '.' in n else n}
        if n.isdigit() and int(n) < len(NUMW): alts.add(NUMW[int(n)])
        if n in NUMW: alts.add(str(NUMW.index(n)))
        return any(x.lstrip('$').rstrip('%') in alts for x in A)
    G = norm(g); return ' '.join(G) in ' '.join(A)
def turns(e):
    ks, tx = [], {}
    order = sorted(range(len(e['haystack_dates'])), key=lambda si: (e['haystack_dates'][si], si)); rk = {si: r / max(1, len(order) - 1) for r, si in enumerate(order)}
    for si, (s, d) in enumerate(zip(e['haystack_sessions'], e['haystack_dates'])):
        for i, t in enumerate(s): ks.append((si, i)); tx[(si, i)] = f"[{d}] {t['role']}: {t['content']}"
    return ks, tx, rk
def contexts(e):
    ks, tx, rk = turns(e); sc = BM([tx[k].split(': ', 1)[1] for k in ks]).score(e['question'])
    bm = sorted(range(len(ks)), key=lambda i: -sc[i]); cand = [i for i in bm[:40] if sc[i] > 0]; m = max([sc[i] for i in cand] or [1])
    rec = sorted(cand, key=lambda i: -(sc[i] / m + 0.3 * rk[ks[i][0]]))
    c1 = fill([(tx[ks[i]], set()) for i in bm], 1024)[0]; c3 = fill([(tx[ks[i]], set()) for i in rec], 1024)[0]
    c768 = fill([(tx[ks[i]], set()) for i in bm], 768)[0]
    topk = fill([(tx[ks[i]][:1500], set()) for i in bm[:40]], 3000)[0]
    return c1, c3, c768, topk
def trunc(t, B):
    out = ''
    for line in t.splitlines():
        p = out + ('\n' if out else '') + line
        if count_tokens(p) > B: break
        out = p
    return out
def main():
    ids = json.load(open(os.environ.get('EXPC_IDS', f'{OUT}/exp-c-ids.json')))['ids']; n = int(sys.argv[1]) if len(sys.argv) > 1 else len(ids)
    D = {e['question_id']: e for e in json.load(open('data/longmemeval_s.json')) if e['question_id'] in ids}
    rows = []
    for qid in ids[:n]:
        e = D[qid]; c1, c3, c768, topk = contexts(e); extra = {'bm25': [], 'recency': [], 'state': []}
        st = call(STATE.format(c=topk, q=e['question']), 400, f'{qid}|state'); extra['state'].append(st)
        c2 = 'STATE (latest values):\n' + trunc(st['text'], 250) + '\n\nRETRIEVED:\n' + c768
        for arm, ctx in (('bm25', c1), ('state', c2), ('recency', c3)):
            r = call(READER.format(c=ctx, d=e['question_date'], q=e['question']), 150, f'{qid}|read|{arm}'); a = r['text']
            kind = exact_kind(e['answer'])
            if kind: ok, votes = exact(e['answer'], a), None
            else:
                votes = [call(GRADE.format(q=e['question'], g=e['answer'], a=a), 5, f'{qid}|grade|{arm}|{v}', temp=0.7, seed=v)['text'].lower().startswith('yes') for v in range(3)]
                ok = sum(votes) >= 2
            cs = extra[arm] + [r]
            rows.append(dict(qid=qid, arm=arm, ok=bool(ok), kind=kind or 'judge', votes=votes, unknown=a.lower().strip(' .') == 'unknown', gold=str(e['answer'])[:80], answer=a[:160],
                             tok=sum(x['pt'] + x['ct'] for x in cs), usd=sum(x['cost'] for x in cs), ctx_tok=count_tokens(ctx)))
            print(qid, arm, int(ok), kind or votes, '|', str(e['answer'])[:40], '|', a[:80], flush=True)
        print('spent', round(spent, 4), flush=True)
    json.dump(rows, open(os.environ.get('EXPC_ROWS', f'{OUT}/expc-rows.json'), 'w'), indent=1); return rows
if __name__ == '__main__': main()
