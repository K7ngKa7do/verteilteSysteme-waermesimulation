from klib import *
def stat(rows,P,N):
    z=col(rows,"zeit_s",P=P,N=N); k=col(rows,"komm_max_s",P=P,N=N); return z,k
def kp(z,k): return {"Median(komm)/Median(zeit)":med(k)/med(z)*100, "Median(komm/zeit)":float(np.median(k/z))*100}
E1=load("e1_groesse_2026-11-01.csv"); print("E1 Zeilen",len(E1))
tab=[("256","0,0134","981","0,0050","65,0","2,65","0,0521","97,4","0,26"),
("512","0,0535","980","0,0135","51,5","3,97","0,0664","96,0","0,80"),
("1024","0,2230","940","0,0320","25,7","6,97","0,0842","91,4","2,65"),
("2048","2,2131","379","0,4416","4,1","5,01","0,1385","79,8","15,98"),
("4096","5,1879","647","1,7864","4,3","2,90","0,4576","50,6","11,34"),
("8192","21,6662","619","7,2347","3,3","2,99","0,1878","50,8","11,53")]
tab[5]=("8192","21,6662","619","7,2347","3,3","2,99","1,8788","50,8","11,53")
for N,p1,u1,p12,k12,s12,p48,k48,s48 in tab:
    N=int(N); z1,_=stat(E1,1,N); z12,kk12=stat(E1,12,N); z48,kk48=stat(E1,48,N)
    chk(f"E1 N={N} P1",p1,med(z1))
    chk_any(f"E1 N={N} Mio Upd/s",u1,{"N^2":N*N*200/med(z1)/1e6,"(N-2)^2":(N-2)**2*200/med(z1)/1e6})
    chk(f"E1 N={N} P12",p12,med(z12)); chk(f"E1 N={N} P48",p48,med(z48))
    chk_any(f"E1 N={N} P12 Komm%",k12,kp(z12,kk12)); chk_any(f"E1 N={N} P48 Komm%",k48,kp(z48,kk48))
    chk(f"E1 N={N} S12",s12,med(z1)/med(z12)); chk(f"E1 N={N} S48",s48,med(z1)/med(z48))
    assert len(z1)==len(z12)==len(z48)==20
print("   [Info] Welche Komm%-Definition passt:",DEFCOUNT); DEFCOUNT.clear()
chk("E1 Fn: S12 gegen Baseline 3,01","3,01",1.3309/med(col(E1,"zeit_s",P=12,N=2048))); chk("E1 Fn: S48 gegen Baseline 9,61","9,61",1.3309/med(col(E1,"zeit_s",P=48,N=2048)))
chk("E1 Befund P=48 N=256 Speedup 0,26","0,26",med(col(E1,'zeit_s',P=1,N=256))/med(col(E1,'zeit_s',P=48,N=256)))
report("E1 (Zeilen 123-139)")
# --- E2
S=load("e2_slot_2026-11-01.csv"); Nd=load("e2_node_2026-11-01.csv")
e2=[("2048","4","0,5048","0,4973","0,5135","0,3850","0,3747","0,3939","1,31","5,3","30,2"),
("2048","8","0,4702","0,4576","0,4750","0,2817","0,2759","0,2860","1,67","11,7","47,1"),
("2048","12","0,4419","0,4410","0,4431","0,2624","0,2575","0,2674","1,68","4,1","60,2"),
("2048","24","0,1751","0,1736","0,1820","0,3575","0,3565","0,3593","0,49","63,4","85,4"),
("4096","4","2,5226","1,9956","2,5652","2,3949","2,3897","2,4087","1,05","32,1","44,6"),
("4096","8","1,7896","1,7799","1,7986","0,9364","0,9322","0,9452","1,91","5,6","25,3"),
("4096","12","1,8031","1,7878","1,8262","0,7892","0,7788","0,8037","2,28","4,2","35,3"),
("4096","24","0,9088","0,9000","0,9208","0,7235","0,7034","0,7486","1,26","42,5","64,1")]
for N,P,sm,slo,shi,nm,nlo,nhi,ratio,ks,kn in e2:
    N=int(N);P=int(P); zs,kS=stat(S,P,N); zn,kN=stat(Nd,P,N); assert len(zs)==len(zn)==20
    l,h=ki(zs); chk(f"E2 N={N} P={P} slot med",sm,med(zs)); chk(f"E2 slot KI lo {N},{P}",slo,l); chk(f"E2 slot KI hi {N},{P}",shi,h)
    l,h=ki(zn); chk(f"E2 N={N} P={P} node med",nm,med(zn)); chk(f"E2 node KI lo {N},{P}",nlo,l); chk(f"E2 node KI hi {N},{P}",nhi,h)
    chk(f"E2 N={N} P={P} slot/node",ratio,med(zs)/med(zn))
    chk_any(f"E2 N={N} P={P} Komm% slot",ks,kp(zs,kS)); chk_any(f"E2 N={N} P={P} Komm% node",kn,kp(zn,kN))
print("   [Info] Komm%-Definition:",DEFCOUNT); DEFCOUNT.clear()
chk("E2 Befund 5,1879/0,7892 = 6,6","6,6",med(col(E1,'zeit_s',P=1,N=4096))/med(col(Nd,'zeit_s',P=12,N=4096)))
chk("E2 Überschlag 6*2*16 KB = 197 KB","197",6*2*2048*8/1000)
chk("E2 Überschlag ms/Schritt 1,7","1,7",6*2*2048*8/117e6*1000)
chk("E2 Überschlag 0,34 s","0,34",6*2*2048*8/117e6*200)
chk("E2 gemessene Austauschzeit 0,31 (85,4 % von 0,3575)","0,31",0.854*med(col(Nd,'zeit_s',P=24,N=2048)))
chk("E2 Überschlag N=4096 0,67","0,67",6*2*4096*8/117e6*200)
chk("E2 gemessen N=4096 P=24 ≈ 0,46 (64,1 % von 0,7235)","0,46",0.641*med(col(Nd,'zeit_s',P=24,N=4096)))
report("E2 (Zeilen 153-171)")
# --- E2b / E2d
Sb=load("e2b_slot_2026-11-01.csv"); Nb=load("e2b_node_2026-11-01.csv"); Pd=load("e2d_ppr_2026-11-01.csv"); print("e2b/e2d Zeilen",len(Sb),len(Nb),len(Pd))
chk("E2b P=2 N=4096 node","2,7927",med(col(Nb,'zeit_s',P=2,N=4096))); chk("E2b P=2 N=4096 slot","2,7938",med(col(Sb,'zeit_s',P=2,N=4096)))
chk("E2b P=2 N=2048 node","0,6902",med(col(Nb,'zeit_s',P=2,N=2048))); chk("E2b P=2 N=2048 slot","0,7256",med(col(Sb,'zeit_s',P=2,N=2048)))
base={2048:1.3309,4096:5.1694}
ppr4096=[(8,"0,8855","5,84","73,0"),(12,"0,7151","7,23","60,2"),(24,"0,5160","10,02","41,7"),(36,"0,4654","11,11","30,9")]
ppr2048=[(8,"0,2711","4,91","61,4"),(12,"0,2106","6,32","52,7"),(24,"0,1601","8,31","34,6"),(36,"0,1460","9,12","25,3")]
A=load("a_strong_2026-10-28.csv")
for N,lst in [(4096,ppr4096),(2048,ppr2048)]:
    for P,pm,pS,pE in lst:
        m=med(col(Pd,'zeit_s',P=P,N=N)); chk(f"E2d N={N} P={P} med",pm,m); chk(f"E2d N={N} P={P} S",pS,base[N]/m); chk(f"E2d N={N} P={P} E%",pE,base[N]/m/P*100)
    m48=med(col(A,'zeit_s',P=48,N=N)); chk(f"E2d N={N} P=48 Referenz (28.10.)", "0,4567" if N==4096 else "0,1409", m48)
    chk(f"E2d N={N} P=48 S",("11,32" if N==4096 else "9,45"),base[N]/m48); chk(f"E2d N={N} P=48 E%",("23,6" if N==4096 else "19,7"),base[N]/m48/48*100)
for N in (2048,4096):
    m48=med(col(A,'zeit_s',P=48,N=N)); m48b=med(col(E1,'zeit_s',P=48,N=N))
    for P in (24,36):
        mp=med(col(Pd,'zeit_s',P=P,N=N)); print(f"   [Info] Anteil an 48er-Geschw. N={N} P={P}: Ref 28.10. {m48/mp*100:.1f} %  | Ref E1 01.11. {m48b/mp*100:.1f} %")
chk("E2d Anteil N=4096 P=36 98,1","98,1",med(col(A,'zeit_s',P=48,N=4096))/med(col(Pd,'zeit_s',P=36,N=4096))*100)
# Reproduzierbarkeit: alle (N,P)-Paare slot 01.11. gegen 28.10.
print("   [Info] Reproduzierbarkeit slot 01.11. gegen 28.10. (%):")
for nm,rows in [("e2",S),("e2b",Sb)]:
    for N in (2048,4096):
        for P in sorted({int(r['P']) for r in rows}):
            a=med(col(A,'zeit_s',P=P,N=N)); b=med(col(rows,'zeit_s',P=P,N=N)); print(f"      {nm} N={N} P={P}: {100*(b-a)/a:+.1f} %")
report("E2b/E2d (Zeilen 208-217)")
# --- E2c
c={}
for mp in ("slot","node"): c[mp]=load(f"e2c_{mp}_2026-11-01.csv")
for P in (4,8,12,24): c[("ppr",P)]=load(f"e2c_ppr_P{P}_2026-11-01.csv")
ref=med(col(E1,'zeit_s',P=1,N=8192)); chk("E2c Referenz P=1 N=8192","21,6662",ref)
e2c=[(4,"slot","8,0718","7,9786","8,1281","2,68","67,1"),(4,"node","6,1661","6,1427","6,2287","3,51","87,8"),(4,"ppr","6,1691","6,1493","6,2248","3,51","87,8"),
(8,"slot","7,2597","7,0720","7,3184","2,98","37,3"),(8,"node","3,5151","3,4887","3,5602","6,16","77,0"),(8,"ppr","3,3648","3,3479","3,3956","6,44","80,5"),
(12,"slot","7,3506","7,2966","7,4821","2,95","24,6"),(12,"node","3,3322","2,9488","5,1119","6,50","54,2"),(12,"ppr","2,5526","2,4995","3,2855","8,49","70,7"),
(24,"slot","3,6896","3,6752","3,7081","5,87","24,5"),(24,"node","2,6041","2,5677","7,9905","8,32","34,7"),(24,"ppr","1,9860","1,9600","2,0573","10,91","45,5")]
for P,mp,pm,plo,phi,pS,pE in e2c:
    rows = c[mp] if mp!="ppr" else c[("ppr",P)]
    v=col(rows,'zeit_s',P=P,N=8192); assert len(v)==20,(mp,P,len(v)); l,h=ki(v)
    chk(f"E2c P={P} {mp} med",pm,med(v)); chk(f"E2c P={P} {mp} KI lo",plo,l); chk(f"E2c P={P} {mp} KI hi",phi,h); chk(f"E2c P={P} {mp} S",pS,ref/med(v)); chk(f"E2c P={P} {mp} E%",pE,ref/med(v)/P*100)
chk("E2c 6,1661 vs 6,1691 Rauschen: Verhältnis 1,31 (P=4 slot/node)","1,31",med(col(c['slot'],'zeit_s',P=4,N=8192))/med(col(c['node'],'zeit_s',P=4,N=8192)))
chk("E2c ppr P=24 94,6 % von P=48 (E1 1,8788)","94,6",med(col(E1,'zeit_s',P=48,N=8192))/med(col(c[('ppr',24)],'zeit_s',P=24,N=8192))*100)
report("E2c (Zeilen 220-232)")
# --- E11 Karp-Flatt
kf={4096:[(2,"0,083"),(4,"0,314"),(8,"0,251"),(12,"0,288"),(24,"0,139"),(36,"0,090"),(48,"0,069")],2048:[(2,"0,089"),(4,"0,171"),(8,"0,250"),(12,"0,271"),(24,"0,096"),(36,"0,092"),(48,"0,087")]}
for N,l in kf.items():
    for P,pe in l:
        Sx=base[N]/med(col(A,'zeit_s',P=P,N=N)); chk(f"E11 N={N} P={P}",pe,(1/Sx-1/P)/(1-1/P))
report("E11 Karp-Flatt (Zeilen 177-178)")
