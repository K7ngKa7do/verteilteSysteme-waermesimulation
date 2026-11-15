from klib import *
E1=load("e1_groesse_2026-11-01.csv")
# --- E3
e3=load("e3_pingpong_2026-11-01.csv"); print("E3 Zeilen",len(e3))
def t3(mod,n): return np.array([float(r["zeit_einfach_s"]) for r in e3 if r["modus"]==mod and int(r["groesse_byte"])==n])
tab=[(8,"1,80","4,4","53,10","0,2"),(64,"1,83","35,0","54,69","1,2"),(512,"2,37","215,8","66,66","7,7"),(4096,"5,73","715,2","123,39","33,2"),(32768,"10,00","3276,4","376,06","87,1"),(262144,"46,81","5599,6","2442,98","107,3"),(1048576,"152,32","6884,2","9114,20","115,0"),(4194304,"522,94","8020,6","35865,01","116,9"),(16777216,"2191,64","7655,1","142789,72","117,5")]
for n,ia,ib,oa,ob in tab:
    ti=med(t3("intra",n)); to=med(t3("inter",n)); assert len(t3("intra",n))==20==len(t3("inter",n))
    chk(f"E3 {n} intra µs",ia,ti*1e6); chk(f"E3 {n} intra MB/s",ib,n/ti/1e6); chk(f"E3 {n} inter µs",oa,to*1e6); chk(f"E3 {n} inter MB/s",ob,n/to/1e6)
l,h=ki(t3("inter",16777216)); chk("E3 KI inter 16MiB lo","142787,9",l*1e6); chk("E3 KI inter 16MiB hi","142791,6",h*1e6)
# Hockney: alpha = Zeit bei 8 B; beta aus Geraden-Anpassung ab 256 KiB (Methode im Protokoll nur grob beschrieben -> zwei Varianten)
sizes=[262144,1048576,4194304,16777216]
for mod,pa,pb in [("intra","1,80","7689"),("inter","53,10","118")]:
    x=np.array(sizes,float); y=np.array([med(t3(mod,n)) for n in sizes])
    a1,b1=np.polyfit(x,y,1)  # y = b*x + a  -> beta = 1/slope
    beta_fit=1/a1/1e6
    # alternative: gewichtete/alle Einzelmessungen
    X=np.concatenate([np.full(20,n,float) for n in sizes]); Y=np.concatenate([t3(mod,n) for n in sizes]); s2,_=np.polyfit(X,Y,1)
    print(f"   [Info] Hockney {mod}: alpha(8 B)={med(t3(mod,8))*1e6:.2f} µs; beta aus Median-Gerade {beta_fit:.0f} MB/s; aus Einzelwerten {1/s2/1e6:.0f} MB/s (Protokoll: {pb})")
    chk(f"E3 Hockney {mod} alpha",pa,med(t3(mod,8))*1e6); chk_any(f"E3 Hockney {mod} beta",pb,{"Median-Gerade":beta_fit,"Einzelwerte":1/s2/1e6})
ai=med(t3("intra",8)); ao=med(t3("inter",8))
print(f"   [Info] Latenzverhältnis {ao/ai:.2f}; Bandbreitenverhältnis (mit β 7689/118): {7689/118:.2f}")
chk("E3 Latenz 29-fach?","29",ao/ai); chk("E3 inter 94 % von 125","94",117.5/125*100)
report("E3 (Zeilen 181-196)")
# Modellvergleich
beta=118e6; alpha=med(t3("inter",8))
mv=[(256,"28,2","50,7","1,80"),(512,"35,2","63,7","1,81"),(1024,"49,1","77,0","1,57"),(2048,"77,0","110,5","1,44"),(4096,"132,8","231,5","1,74"),(8192,"244,3","954,4","3,91")]
for N,pm,pg,pf in mv:
    z=col(E1,'zeit_s',P=48,N=N); k=col(E1,'komm_max_s',P=48,N=N)
    model=2*(alpha+8*N/beta)*200*1000
    chk_any(f"Modell N={N}",pm,{"β=118":model,"β=117,5":2*(alpha+8*N/117.5e6)*200*1000})
    g={"Med(k)":med(k)*1000,"Med(k)/Med(z)*Med(z)":med(k)/med(z)*med(z)*1000,"Med(k/z)*Med(z)":float(np.median(k/z))*med(z)*1000}
    chk_any(f"Gemessen N={N}",pg,g)
    chk_any(f"Faktor N={N}",pf,{"Faktor":med(k)*1000/model, "Faktor(prot.Zahlen)":num(pg)/num(pm)})
print("   [Info]",DEFCOUNT); DEFCOUNT.clear()
report("E3 Modellvergleich (Zeile 197)")
# --- E10
e10=load("e10_bandbreite_2026-11-01.csv"); print("E10 Zeilen",len(e10),"Modi",sorted({r['modus'] for r in e10}))
def g10(m,P,k="gb_summe"): return np.array([float(r[k]) for r in e10 if r["modus"]==m and int(r["P"])==P])
e10t=[("ein_rechner",1,"13,27","13,21","13,31",None),("ein_rechner",2,"23,20",None,None,"11,60"),("ein_rechner",4,"39,71",None,None,"9,93"),("ein_rechner",6,"46,05",None,None,"7,67"),("ein_rechner",8,"48,04","47,87","48,18","6,00"),("ein_rechner",12,"46,84","46,70","46,97","3,90"),
("vier_rechner",4,"52,68",None,None,"13,17"),("vier_rechner",8,"92,04",None,None,"11,51"),("vier_rechner",12,"126,59",None,None,"10,55"),("vier_rechner",24,"181,88","181,38","181,97","7,58"),("vier_rechner",48,"185,30","184,77","185,77","3,86")]
for m,P,pm,plo,phi,pp in e10t:
    v=g10(m,P); assert len(v)==20,(m,P,len(v)); chk(f"E10 {m} P={P} GB/s",pm,med(v))
    if plo: l,h=ki(v); chk(f"E10 {m} P={P} KI lo",plo,l); chk(f"E10 {m} P={P} KI hi",phi,h)
    if pp: chk_any(f"E10 {m} P={P} je Prozess",pp,{"Median(gb_pro_prozess)":med(g10(m,P,'gb_pro_prozess')),"Median(summe)/P":med(v)/P})
chk("E10 −71 %","71",(1-med(g10('ein_rechner',12))/P_ if False else 1-3.90/13.27)*100) if False else None
chk("E10 −71 % (je Prozess 13,3->3,9)","71",(1-med(g10('ein_rechner',12,'gb_pro_prozess'))/med(g10('ein_rechner',1,'gb_pro_prozess')))*100)
chk("E10 96 % von 4*48,04","96",med(g10('vier_rechner',48))/(4*med(g10('ein_rechner',8)))*100)
chk("E10 4*48,04 = 192,2","192,2",4*med(g10('ein_rechner',8)))
chk("E10 P=24 = 98 % von P=48","98",med(g10('vier_rechner',24))/med(g10('vier_rechner',48))*100)
chk("E7 Obergrenze 185,3/13,27 ≈ 14","14",med(g10('vier_rechner',48))/med(g10('ein_rechner',1)))
report("E10 (Zeilen 235-241, 310)")
# --- E9
c={}
c["slot"]=load("e2c_slot_2026-11-01.csv")
for P in (4,8,12,24): c[P]=load(f"e2c_ppr_P{P}_2026-11-01.csv")
U=8192*8192*200
chk("E9 13,42e9 Updates","13,42",U/1e9)
def copy_el(m,P): return med(g10(m,P))*1e9/16
rows=[("slot",1,"0,619","75",med(col(E1,'zeit_s',P=1,N=8192)),'ein_rechner'),("slot",4,"1,663","67",med(col(c['slot'],'zeit_s',P=4,N=8192)),'ein_rechner'),("slot",8,"1,849","62",med(col(c['slot'],'zeit_s',P=8,N=8192)),'ein_rechner'),("slot",12,"1,826","62",med(col(c['slot'],'zeit_s',P=12,N=8192)),'ein_rechner'),
("ppr",4,"2,176","66",med(col(c[4],'zeit_s',P=4,N=8192)),'vier_rechner'),("ppr",8,"3,989","69",med(col(c[8],'zeit_s',P=8,N=8192)),'vier_rechner'),("ppr",12,"5,258","66",med(col(c[12],'zeit_s',P=12,N=8192)),'vier_rechner'),("ppr",24,"6,758","59",med(col(c[24],'zeit_s',P=24,N=8192)),'vier_rechner'),("ppr",48,"7,144","62",med(col(E1,'zeit_s',P=48,N=8192)),'vier_rechner')]
for kind,P,pu,pq,t,mode in rows:
    ups=U/t/1e9; chk(f"E9 {kind} P={P} Mrd Upd/s",pu,ups); chk(f"E9 {kind} P={P} Anteil %",pq,ups*1e9/copy_el(mode,P)*100)
chk("E9 9,9 GB/s","9,9",U/med(col(E1,'zeit_s',P=1,N=8192))*16/1e9); chk("E9 14,9 GB/s","14,9",U/med(col(E1,'zeit_s',P=1,N=8192))*24/1e9)
report("E9 (Zeilen 243, 257-261)")
