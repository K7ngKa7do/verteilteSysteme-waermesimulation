import csv, glob, os, math, sys
import numpy as np
base = os.path.expanduser("~/mnt/waerme_sicherung_2026-11-01/results")
def ci(v):
    v = sorted(v); n = len(v)
    if n < 11: return (v[0], v[-1])
    lo = math.floor((n - 1.96*math.sqrt(n))/2); hi = math.ceil(1 + (n + 1.96*math.sqrt(n))/2)
    return (v[max(lo,1)-1], v[min(hi,n)-1])
def zwei_zustaende(v):
    v = np.sort(np.array(v)); n=len(v)
    best=(1.0,None)
    for k in range(3, n-2):   # beide Gruppen >=3
        r = v[k]/v[k-1]
        if r>best[0]: best=(r,k)
    return best
rows_out=[]
for f in sorted(glob.glob(base+"/e*_2026-11-01.csv")):
    name=os.path.basename(f).replace("_2026-11-01.csv","")
    if name.startswith(("e3_","e10_","e13")): continue
    d={}
    for r in csv.DictReader(open(f)):
        d.setdefault((int(r["P"]),int(r["N"])),[]).append(float(r["zeit_s"]))
    for (P,N),v in sorted(d.items()):
        med=float(np.median(v)); lo,hi=ci(v)
        g,k=zwei_zustaende(v)
        rows_out.append((name,P,N,len(v),med,lo,hi,(hi-lo)/med*100,min(v),max(v),max(v)/min(v),g))
print("datei;P;N;n;median;ki_lo;ki_hi;ki_breite_%;min;max;max/min;groesste_luecke")
for r in rows_out:
    print(";".join(f"{x:.4f}" if isinstance(x,float) else str(x) for x in r))
