import csv, os, math, re
import numpy as np
B = os.path.expanduser("~/mnt/waerme_sicherung_2026-11-01")
R = B + "/results"
def load(fname, folder=R):
    return list(csv.DictReader(open(f"{folder}/{fname}")))
def col(rows, key, **flt):
    out=[]
    for r in rows:
        if all(float(r[k])==v for k,v in flt.items()): out.append(float(r[key]))
    return np.array(out)
def ki(v):
    v=sorted(v); n=len(v)
    lo=math.floor((n-1.96*math.sqrt(n))/2); hi=math.ceil(1+(n+1.96*math.sqrt(n))/2)
    return v[max(lo,1)-1], v[min(hi,n)-1]
def med(v): return float(np.median(v))
ERR=[]; N_OK=[0]
def num(s):
    s=s.replace("−","-").replace(" ","").replace(" ","")
    return float(s.replace(",","."))
def dec(s):
    s=s.replace(" ","").replace(",",".")
    m=re.search(r"e[+-]?\d+$",s)
    mant=s[:m.start()] if m else s
    return len(mant.split(".")[1]) if "." in mant else 0
def chk(label, proto, new, scale=1.0):
    """proto: Text wie im Protokoll (z.B. '2,2092' oder '60,2'). new: neu berechneter Wert (schon in gleicher Einheit)."""
    p=num(proto); d=dec(proto)
    ok = abs(round(new*scale,d)-p) <= 10**(-d)*0.5+1e-12 or abs(new*scale-p) <= 0.5*10**(-d)+1e-12
    if ok: N_OK[0]+=1
    else: ERR.append((label, proto, new*scale))
    return ok
def report(title):
    print(f"== {title}: {N_OK[0]} Werte stimmen, {len(ERR)} Abweichungen")
    for e in ERR: print("   ABWEICHUNG:", e[0], "| Protokoll:", e[1], "| neu:", (f"{e[2]:.6g}" if not isinstance(e[2],str) else e[2]))
    ERR.clear(); N_OK[0]=0
DEFCOUNT={}
ONLY_OTHER=[]
def chk_any(label, proto, cands):
    """cands: dict name->Wert; ok wenn mindestens einer passt; zählt, welche Definition passt"""
    p=num(proto); d=dec(proto); hit=[]
    for k,v in cands.items():
        if abs(round(v,d)-p) <= 10**(-d)*0.5+1e-12 or abs(v-p)<=0.5*10**(-d)+1e-12: hit.append(k)
    for k in hit: DEFCOUNT[k]=DEFCOUNT.get(k,0)+1
    if "Komm%" in label:
        first=list(cands)[0]
        if first not in hit: ONLY_OTHER.append((label,proto,hit))
    if hit: N_OK[0]+=1
    else: ERR.append((label,proto,"; ".join(f"{k}={v:.5g}" for k,v in cands.items())))
