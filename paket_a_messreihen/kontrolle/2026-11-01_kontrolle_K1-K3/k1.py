from klib import *
K = B + "/kadan"
# --- A4: test.csv / test20.csv
t=load("test.csv",K)
def sel(rows,P,N): return np.array([float(r["zeit_s"]) for r in rows if int(r["P"])==P and int(r["N"])==N])
for N,exp in [(512,[("1","0,0536",None,None),("2","0,0327","1,64","82"),("4","0,0210","2,55","64")]),(1024,[("1","0,2231",None,None),("2","0,1221","1,83","91"),("4","0,0699","3,19","80")])]:
    m1=med(sel(t,1,N))
    for P,pm,ps,pe in exp:
        m=med(sel(t,int(P),N)); chk(f"A4 N={N} P={P} Median",pm,m)
        if ps: chk(f"A4 N={N} P={P} S",ps,m1/m); chk(f"A4 N={N} P={P} E%",pe,m1/m/int(P)*100)
t2=load("test20.csv",K)
for P,pm,pmin,lo,hi in [(1,"0,2234","0,2217","0,2222","0,2243"),(4,"0,0709","0,0701","0,0703","0,0712")]:
    v=sel(t2,P,1024); l,h=ki(v)
    chk(f"A4 test20 P={P} Median",pm,med(v)); chk(f"A4 test20 P={P} Min",pmin,v.min()); chk(f"A4 test20 P={P} KI lo",lo,l); chk(f"A4 test20 P={P} KI hi",hi,h)
v1=sel(t2,1,1024); v4=sel(t2,4,1024); chk("A4 test20 S","3,15",med(v1)/med(v4)); chk("A4 test20 E%","79",med(v1)/med(v4)/4*100)
print("test20 Zeilen:",len(t2))
# --- A5 Baseline
b=load("baseline.csv",K)
def bsel(mod,N): return np.array([float(r["zeit_s"]) for r in b if r["modus"]==mod and int(r["N"])==N])
for mod,N,pm,plo,phi,pu in [("numba",2048,"1,3309","1,3172","1,3435","629"),("numba",4096,"5,1694","5,1251","5,2254","648"),("numpy",2048,"10,7618","10,5780","10,8477","78")]:
    v=bsel(mod,N); l,h=ki(v)
    chk(f"Baseline {mod} {N} Median",pm,med(v)); chk(f"Baseline {mod} {N} KI lo",plo,l); chk(f"Baseline {mod} {N} KI hi",phi,h)
    chk(f"Baseline {mod} {N} Mio Upd/s (innere Zellen (N-2)^2)",pu,(N-2)**2*200/med(v)/1e6)
    print(f"   [Info] {mod} {N}: Mio Upd/s mit N^2: {N*N*200/med(v)/1e6:.1f}; mit (N-2)^2: {(N-2)**2*200/med(v)/1e6:.1f}")
chk("NumPy/Numba Faktor 2048","8,1",med(bsel('numpy',2048))/med(bsel('numba',2048)))
report("A4/A5 (test, test20, baseline)")
# --- A6/A7 Strong 28.10.
s=load("a_strong_2026-10-28.csv"); print("a_strong Zeilen:",len(s))
strong={2048:"P1 2,2092 (2,1496–2,2121) 1,00 100 % 0,0036 · P2 0,7244 (0,7159–0,7262) 3,05 152 % 0,0170 · P4 0,5034 (0,5007–0,5144) 4,39 110 % 0,0291 · P8 0,4577 (0,4533–0,4620) 4,83 60 % 0,0394 · P12 0,4421 (0,4413–0,4429) 5,00 42 % 0,0183 · P24 0,1777 (0,1742–0,1839) 12,43 52 % 0,1129 · P36 0,1561 (0,1450–0,1588) 14,15 39 % 0,1188 · P48 0,1409 (0,1367–0,1453) 15,67 33 % 0,1129",
 4096:"P1 5,1909 (5,1857–5,1949) 1,00 100 % 0,0040 · P2 2,8003 (2,7887–2,8045) 1,85 93 % 0,0290 · P4 2,5081 (1,9289–2,5329) 2,07 52 % 0,8105 · P8 1,7799 (1,7656–1,8004) 2,92 36 % 0,1136 · P12 1,7953 (1,7757–1,8212) 2,89 24 % 0,0789 · P24 0,9063 (0,8866–0,9207) 5,73 24 % 0,3441 · P36 0,5970 (0,5958–0,5995) 8,69 24 % 0,2470 · P48 0,4567 (0,4555–0,4581) 11,37 24 % 0,2341"}
pat=re.compile(r"P(\d+) ([\d,]+) \(([\d,]+)–([\d,]+)\) ([\d,]+) (\d+) % ([\d,]+)")
medS={}
for N,txt in strong.items():
    ms=pat.findall(txt); m1=med(col(s,"zeit_s",P=1,N=N))
    for P,pm,plo,phi,pS,pE,pK in ms:
        P=int(P); v=col(s,"zeit_s",P=P,N=N); k=col(s,"komm_max_s",P=P,N=N); l,h=ki(v); medS[(N,P)]=med(v)
        assert len(v)==20,(N,P,len(v))
        chk(f"Strong N={N} P={P} Median",pm,med(v)); chk(f"Strong N={N} P={P} KI lo",plo,l); chk(f"Strong N={N} P={P} KI hi",phi,h)
        chk(f"Strong N={N} P={P} S",pS,m1/med(v)); chk(f"Strong N={N} P={P} E%",pE,m1/med(v)/P*100); chk(f"Strong N={N} P={P} Komm.max-Median",pK,med(k))
report("A7 Strong-Scaling-Tabellen (Zeilen 41, 44)")
# Weak
w=load("a_weak_2026-10-28.csv")
for P,N,pm,plo,phi,pe,pu in [(12,4096,"1,8174","1,7869","1,8455","100","1845"),(24,5793,"1,7652","1,7560","1,7807","103","3800"),(48,8192,"1,8200","1,8156","1,8237","100","7371")]:
    v=col(w,"zeit_s",P=P,N=N); l,h=ki(v); m1=med(col(w,"zeit_s",P=12,N=4096))
    assert len(v)==20
    chk(f"Weak P={P} Median",pm,med(v)); chk(f"Weak P={P} KI lo",plo,l); chk(f"Weak P={P} KI hi",phi,h)
    chk(f"Weak P={P} E%",pe,m1/med(v)*100); chk(f"Weak P={P} Mio Upd/s (N^2)",pu,N*N*200/med(v)/1e6)
    print(f"   [Info] Weak P={P}: Mio Upd/s mit N^2 {N*N*200/med(v)/1e6:.1f}, mit (N-2)^2 {(N-2)**2*200/med(v)/1e6:.1f}, E% {m1/med(v)*100:.2f}")
report("A6/A7 Weak Scaling (Zeile 46, 96)")
# Teil 7 Tabelle (Baseline-Bezug)
bn={2048:1.3309,4096:5.1694}
rows7=[("1","2,2092","0,60","60,2","5,1909","1,00","99,6"),("2","0,7244","1,84","91,9","2,8003","1,85","92,3"),("4","0,5034","2,64","66,1","2,5081","2,06","51,5"),("8","0,4577","2,91","36,4","1,7799","2,90","36,3"),("12","0,4421","3,01","25,1","1,7953","2,88","24,0"),("24","0,1777","7,49","31,2","0,9063","5,70","23,8"),("36","0,1561","8,52","23,7","0,5970","8,66","24,1"),("48","0,1409","9,44","19,7","0,4567","11,32","23,6")]
bmed={2048:med(bsel('numba',2048)),4096:med(bsel('numba',4096))}
for P,m1_,s1_,e1_,m2_,s2_,e2_ in rows7:
    P=int(P)
    for N,(pm,ps,pe) in [(2048,(m1_,s1_,e1_)),(4096,(m2_,s2_,e2_))]:
        m=medS[(N,P)]; S=bmed[N]/m
        chk(f"T7 N={N} P={P} Median",pm,m); chk(f"T7 N={N} P={P} S",ps,S); chk(f"T7 N={N} P={P} E%",pe,S/P*100)
report("A7 Teil 7 Tabelle (Zeilen 76-85), Baseline aus baseline.csv")
# Befunde
chk("Befund Faktor 4096 P12->24->48 (Zeile 93) 2,88->5,70->11,32: P12 S","2,88",bmed[4096]/medS[(4096,12)]); chk("P24 S","5,70",bmed[4096]/medS[(4096,24)]); chk("P48 S","11,32",bmed[4096]/medS[(4096,48)])
chk("Faktor 1,98 je Verdopplung (11,32/2,88)^0.5","1,98",((bmed[4096]/medS[(4096,48)])/(bmed[4096]/medS[(4096,12)]))**0.5)
chk("N=2048 P12->24 Faktor 2,5 (7,49/3,01)","2,5",(bmed[2048]/medS[(2048,24)])/(bmed[2048]/medS[(2048,12)]))
chk("Zeile 49: P12 1,803->1,795 (28.10.)","1,795",medS[(4096,12)]); chk("P24 0,906","0,906",medS[(4096,24)]); chk("P48 0,457","0,457",medS[(4096,48)]); chk("Speedup 11,37","11,37",medS[(4096,1)]/medS[(4096,48)])
# A7 Teil 2 Einzelwerte
v=np.sort(col(s,"zeit_s",P=1,N=2048)); print("   [Info] N=2048 P=1 sortiert:",np.round(v,3).tolist())
fast=v[v<1.8]; slow=v[v>=1.8]; print(f"   [Info] schnell n={len(fast)} {fast.min():.3f}-{fast.max():.3f}, langsam n={len(slow)} {slow.min():.3f}-{slow.max():.3f}, Faktor {med(slow)/med(fast):.2f}")
v=np.sort(col(s,"zeit_s",P=4,N=4096)); fast=v[v<2.2]; slow=v[v>=2.2]
print(f"   [Info] N=4096 P=4: schnell n={len(fast)} {fast.min():.3f}-{fast.max():.3f}, langsam n={len(slow)} {slow.min():.3f}-{slow.max():.3f}, Faktor {med(slow)/med(fast):.2f}")
print(f"   [Info] N=2048 P=2: {col(s,'zeit_s',P=2,N=2048).min():.3f}-{col(s,'zeit_s',P=2,N=2048).max():.3f}; N=4096 P=2: {col(s,'zeit_s',P=2,N=4096).min():.3f}-{col(s,'zeit_s',P=2,N=4096).max():.3f}")
report("A7 Befunde Zeilen 49-94")
