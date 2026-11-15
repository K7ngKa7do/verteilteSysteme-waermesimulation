from klib import *
E1=load("e1_groesse_2026-11-01.csv"); Pd=load("e2d_ppr_2026-11-01.csv")
def ppr_med(P,N):
    if P==48: return med(col(E1,'zeit_s',P=48,N=N))
    if N==8192: return med(col(load(f"e2c_ppr_P{P}_2026-11-01.csv"),'zeit_s',P=P,N=N))
    return med(col(Pd,'zeit_s',P=P,N=N))
base={2048:1.3309,4096:5.1694,8192:med(col(E1,'zeit_s',P=1,N=8192))}
# --- E7
e7={2048:("0,0841","11,9",[(8,"4,91","5,04"),(12,"6,32","6,23"),(24,"8,31","8,18"),(36,"9,11","9,13"),(48,"9,61","9,69")]),
    4096:("0,0651","15,4",[(8,"5,84","5,49"),(12,"7,23","6,99"),(24,"10,02","9,61"),(36,"11,11","10,98"),(48,"11,30","11,82")]),
    8192:("0,0599","16,7",[(4,"3,51","3,39"),(8,"6,44","5,64"),(12,"8,49","7,23"),(24,"10,91","10,10"),(48,"11,53","12,58")])}
grid=np.linspace(0,0.5,50001)
for N,(ps,pmax,pts) in e7.items():
    Ps=np.array([p[0] for p in pts],float); S=np.array([base[N]/ppr_med(int(P),N) for P in Ps])
    for lab,PP,SS in [("Punkte der Liste",Ps,S),("zusätzlich P=1 (S=1)",np.append(1,Ps),np.append(1,S))]:
        sse=[np.sum((SS-1/(s+(1-s)/PP))**2) for s in grid[::1]]
        s_fit=grid[int(np.argmin(sse))]
        print(f"   [Info] E7 N={N} {lab}: s_fit={s_fit:.4f}, S_max={1/s_fit:.1f}  (Protokoll s={ps}, S_max={pmax})")
        if lab=="Punkte der Liste":
            chk(f"E7 N={N} s",ps,s_fit); chk(f"E7 N={N} S_max",pmax,1/s_fit)
            for P,pm,pa in pts:
                chk(f"E7 N={N} P={int(P)} gemessen",pm,base[N]/ppr_med(int(P),N)); chk(f"E7 N={N} P={int(P)} Amdahl",pa,1/(s_fit+(1-s_fit)/P))
            dev=max(abs((base[N]/ppr_med(int(P),N))-1/(s_fit+(1-s_fit)/P)) for P in Ps); print(f"   [Info] größte Abweichung N={N}: {dev:.2f}")
report("E7 (Zeilen 304-310)")
# --- E13
def runs(z):
    L=[];c=1
    for i in range(1,len(z)):
        if z[i]==z[i-1]: c+=1
        else: L.append((z[i-1],c)); c=1
    L.append((z[-1],c)); return L
def e13(fname,N,P,pmin,pmed,pmax,pref,pn,ppct,pmedslow,pmedfast,pfac,psw,pexp,pls,plf,pthr=None):
    v=col(load(fname),'zeit_s',P=P,N=N); assert len(v)==200,len(v)
    ref=med(np.sort(v)[:20]); thr=1.15*ref; z=v>thr
    chk(f"E13 {fname} min",pmin,v.min()); chk(f"E13 median",pmed,med(v)); chk("E13 max",pmax,v.max()); chk("E13 Ref schnell",pref,ref)
    if pthr: chk("E13 Schwelle",pthr,thr)
    chk("E13 n langsam",pn,z.sum()); chk("E13 % langsam",ppct,z.mean()*100)
    chk("E13 Median langsam",pmedslow,med(v[z])); chk("E13 Median schnell(langsam-Faktor Basis)",pmedfast,med(v[~z])); chk("E13 Faktor",pfac,med(v[z])/med(v[~z]))
    sw=int(np.sum(z[1:]!=z[:-1])); p=z.mean(); chk("E13 Wechsel",psw,sw); chk("E13 erwartet",pexp,2*p*(1-p)*(len(v)-1))
    r=runs(z); chk("E13 längste Serie langsam",pls,max(c for s,c in r if s)); chk("E13 längste Serie schnell",plf,max(c for s,c in r if not s))
e13("e13_N2048_P1_2026-11-01.csv",2048,1,"1,3017","2,2070","2,2241","1,3259","149","74,5","2,2092","1,3341","1,66","74","75,6","14","3")
e13("e13_N4096_P4_2026-11-01.csv",4096,4,"1,8876","2,5161","2,6311","1,9180","119","59,5","2,5445","1,9623","1,30","93","95,9","11","5","2,2057")
report("E13 (Zeilen 315-321)")
# --- E13b
r=load("e13b_cpu_N2048_P1_2026-11-01.csv"); print("E13b Spalten",list(r[0].keys()),len(r))
v=np.array([float(x['zeit_s']) for x in r]); ref=med(np.sort(v)[:20]); z=v>1.15*ref
chk("E13b langsam n","140",z.sum()); chk("E13b %","70,0",z.mean()*100); chk("E13b Ref","1,3262",ref); chk("E13b Median langsam","2,2077",med(v[z]))
cs=np.array([int(x['cpu_start']) for x in r]); ce=np.array([int(x['cpu_ende']) for x in r])
chk("E13b Kern0 n","193",(cs==0).sum()); chk("E13b Kern0 langsam","135",(z&(cs==0)).sum()); chk("E13b Kern0 %","69,9",(z&(cs==0)).sum()/(cs==0).sum()*100)
chk("E13b Kern1 n","7",(cs==1).sum()); chk("E13b Kern1 langsam","5",(z&(cs==1)).sum()); chk("E13b Kern1 %","71,4",(z&(cs==1)).sum()/(cs==1).sum()*100)
chk("E13b Kernwechsel langsam %","7,1",(z&(cs!=ce)).sum()/z.sum()*100); chk("E13b Kernwechsel schnell %","3,3",((~z)&(cs!=ce)).sum()/(~z).sum()*100)
mh=np.array([float(x['mhz_start']) for x in r]); print(f"   [Info] Frequenz kHz: min {mh.min():.0f} max {mh.max():.0f}; Sockel-Werte {sorted({x['sockel'] for x in r})}; Zwilling {sorted({x['zwilling'] for x in r})}")
report("E13b (Zeilen 325-327)")
