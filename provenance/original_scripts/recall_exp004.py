import json, math, re, sys, collections
sys.path.insert(0, '../asm-next-exp003')
from asm_lab.personal_facts import PersonalMemory, tokens, count_tokens
R = '../asm-next-exp003/runs/'
H = {'45dc21b6':'exp003-check1','26bdc477':'exp003-check1','8fb83627':'exp003-check1','ce6d2d27':'exp003-pilot',
     '2698e78f':'exp003-pilot','2133c1b5':'exp003-pilot','ba61f0b9':'exp003-pilot'}
STOP = set("a an the and or but if of to in on at for with by from as is are was were be been being am i me my mine we our you your he she it its they them their this that these those do does did have has had what which who whom how when where why can could would should will shall may might not no so than too very just about into over also there here all any some more most such only own same then once up down out off again further s t don now".split())
def tok(t): return [w for w in re.findall(r'[^\W_]+', t.casefold()) if w not in STOP]
class BM:
    def __init__(s, docs, k1=1.2, b=.75):
        s.d=[collections.Counter(tok(x)) for x in docs]; s.l=[sum(c.values()) for c in s.d]; s.av=sum(s.l)/max(1,len(s.l)); N=len(docs)
        df=collections.Counter(w for c in s.d for w in c); s.idf={w:math.log(1+(N-n+.5)/(n+.5)) for w,n in df.items()}; s.k1,s.b=k1,b
    def score(s,q):
        qs=set(tok(q)); return [sum(s.idf[w]*c[w]*(s.k1+1)/(c[w]+s.k1*(1-s.b+s.b*L/s.av)) for w in qs if w in c) for c,L in zip(s.d,s.l)]
def fill(items, B):  # items: (text, covers set) ranked
    text, cov = '', set()
    for t, c in items[:300]:
        p = text + ('\n' if text else '') + t
        if count_tokens(p) <= B: text, cov = p, cov | c
    return text, cov
def ranked_b(facts, q):
    fs = [f for f in facts if f['kind'] != 'assistant_said']
    slots = collections.defaultdict(list)
    for f in sorted(fs, key=lambda f: (PersonalMemory.effective(f), f.get('ordinal', 0))):
        slots[(f['kind'], f['subject'].casefold(), f['key'].casefold())].append(f)
    latest = [(h[-1], len(h)) for h in slots.values()]
    docs = [f"{f['key']} {str(f['value'])[:200]}" for f, _ in latest]
    sc = BM(docs).score(q); sc = [x * (1.2 if n > 1 else 1) for x, (f, n) in zip(sc, latest)]
    return [latest[i][0] for i in sorted(range(len(latest)), key=lambda i: (-sc[i], -i))]
def contexts(e, facts, B):
    q = e['question']; turns = {(sid, i): t for sid, s in zip(e['haystack_session_ids'], e['haystack_sessions']) for i, t in enumerate(s)}
    dates = dict(zip(e['haystack_session_ids'], e['haystack_dates']))
    out = {}
    m = PersonalMemory(); m.facts = list(facts); a = m.build(q, B)['text']
    cov = {k for k in turns if re.search(rf"session {re.escape(k[0])} turn {k[1]}\]", a)}
    out['a'] = (a, cov)
    rb = ranked_b(facts, q)
    out['b'] = fill([(f"[stated {f['observed_at']}; occurred {f['event_date'] or 'unknown'}] {f['subject']} / {f['key']} = {str(f['value'])[:200]}", {(f['session_id'], f['source_turn'])}) for f in rb], B)
    seen, it = set(), []
    for f in rb:
        k = (f['session_id'], f['source_turn'])
        if k in seen or k not in turns: continue
        seen.add(k); it.append((f"[{dates[k[0]]}] {turns[k]['role']}: {turns[k]['content']}", {k}))
    out['c'] = fill(it, B)
    keys = list(turns); sc = BM([turns[k]['content'] for k in keys]).score(q)
    out['d'] = fill([(f"[{dates[keys[i][0]]}] {turns[keys[i]]['role']}: {turns[keys[i]]['content']}", {keys[i]}) for i in sorted(range(len(keys)), key=lambda i: -sc[i])], B)
    return out
if __name__ == '__main__':
    D = {e['question_id']: e for e in json.load(open('data/longmemeval_s.json')) if e['question_id'] in H}
    res = {}
    for qid, run in H.items():
        e = D[qid]; facts = json.load(open(f'{R}{run}/facts_{qid}.json'))
        dates = dict(zip(e['haystack_session_ids'], e['haystack_dates']))
        need = [(sid, i) for sid, s in zip(e['haystack_session_ids'], e['haystack_sessions']) for i, t in enumerate(s) if t.get('has_answer')]
        last = max(need, key=lambda k: dates[k[0]])
        for B in (512, 1024):
            for v, (txt, cov) in contexts(e, facts, B).items():
                res[f'{qid}|{B}|{v}'] = dict(latest=int(last in cov), all=sum(k in cov for k in need)/len(need), tok=count_tokens(txt))
    json.dump(res, open('../asm-next-exp003/experiments/exp004/recall.json', 'w'), indent=1)
    for B in (512, 1024):
        print(f'B={B}  latest/all per variant a b c d')
        for qid in H: print(qid, '  '.join(f"{v}:{res[f'{qid}|{B}|{v}']['latest']}/{res[f'{qid}|{B}|{v}']['all']:.2f}" for v in 'abcd'))
        for v in 'abcd': print(' sum', v, sum(res[f'{q}|{B}|{v}']['latest'] for q in H), round(sum(res[f'{q}|{B}|{v}']['all'] for q in H), 2))
