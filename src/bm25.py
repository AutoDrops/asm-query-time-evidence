"""BM25 ranker, greedy token-budget filler and approximate token counter (vendored from the experiment code; no ASM core)."""
import math, re, collections
def count_tokens(text):  # deterministic approximation: 1 token per 4 characters
    return 0 if not text else max(1, math.ceil(len(text) / 4))
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
