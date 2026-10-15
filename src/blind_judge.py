# EXP-C3 blind independent judge (non-Qwen: openai/gpt-4o-mini). Arm identity hidden: each (question, answer) graded alone, shuffled order,
# cache key has no arm. Rules fixed before any call (see BLIND_RULES). Also free FINAL-number rule.
import os, json, random, re, hashlib, sys
OUT = os.environ.get('ASM_OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')); os.environ['EXPC_LED'] = f'{OUT}/blind-ledger.jsonl'
import exp_c as X
X.MODEL = 'openai/gpt-4o-mini'
RULES = ("You are grading an answer against a reference. Rules:\n"
 "1. Numbers/amounts/counts: the answer's FINAL stated value must equal the reference (units may differ only by format, e.g. $50 = 50 dollars). Listing components without stating the correct total = NO. A range is NO unless it is exactly the reference.\n"
 "2. Dates/durations: must match the reference value (equivalent formats ok).\n"
 "3. Lists/sets: must contain all reference items and no contradicting items; missing any = NO.\n"
 "4. Partial, hedged-between-options, or 'unknown' = NO.\n"
 "5. Extra correct detail is fine.\n\nQuestion: {q}\nReference answer: {g}\nModel answer: {a}\n\nReply with exactly YES or NO.")
NUM = re.compile(r'\$?\d[\d,]*\.?\d*')
def final_num(g, a):
    n = X.norm(str(g))[0].lstrip('$').rstrip('%'); xs = [x.replace(',', '').lstrip('$').rstrip('.') for x in NUM.findall(a)]
    words = {w: str(i) for i, w in enumerate(X.NUMW)}; ws = [words[w] for w in X.norm(a) if w in words]
    v = xs[-1] if xs else (ws[-1] if ws else None); nn = words.get(n, n)
    try: return v is not None and float(v) == float(nn)
    except: return v == nn
ids = json.load(open(f'{OUT}/exp-c2-ids.json'))['ids']
D = {e['question_id']: e for e in json.load(open(os.environ.get('LME_S_PATH', 'data/longmemeval_s.json'))) if e['question_id'] in ids}
items = [(r['qid'], r['arm'], r['answer']) for r in json.load(open(f'{OUT}/sens-judge-all-rows.json'))]
items += [(r['qid'], r['arm'], r['answer']) for r in json.load(open(f'{OUT}/expc3-rows.json'))]
random.Random(7).shuffle(items)
from concurrent.futures import ThreadPoolExecutor
def one(it):
    qid, arm, a = it
    e = D[qid]; v = [X.call(RULES.format(q=e['question'], g=e['answer'], a=a), 3, 'blind', temp=0.7, seed=s)['text'].upper().startswith('YES') for s in range(3)]
    return (dict(qid=qid, arm=arm, blind=sum(v) >= 2, votes=v, finalnum=final_num(e['answer'], a) if X.exact_kind(e['answer']) == 'number' else None))
out = list(ThreadPoolExecutor(12).map(one, items))
json.dump(out, open(f'{OUT}/blind-rows.json', 'w'), indent=1); print('spent', X.spent)
