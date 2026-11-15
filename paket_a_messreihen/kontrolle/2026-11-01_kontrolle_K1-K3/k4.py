from klib import *
E1=load("e1_groesse_2026-11-01.csv")
def strip(P,N):
    if P==48: return E1
    if N==8192: return load(f"e2c_ppr_P{P}_2026-11-01.csv")
    return load("e2d_ppr_2026-11-01.csv")
def ci_overlap(a,b):
    la,ha=ki(a); lb,hb=ki(b); return not (ha<lb or hb<la)
def jn(b): return "ja" if b else "nein"
# --- E4
E4={P:load(f"e4_bloecke_P{P}_2026-11-01.csv") for P in (12,24,48)}
e4=[(2048,12,"0,2106","0,2044","0,971","nein","52,7","57,3"),(2048,24,"0,1601","0,1401","0,875","nein","67,5","69,0"),(2048,48,"0,1385","0,1180","0,852","nein","79,8","81,5"),
(4096,12,"0,7151","0,7022","0,982","ja","30,0","27,8"),(4096,24,"0,5160","0,5894","1,142","nein","42,2","35,8"),(4096,48,"0,4576","0,4915","1,074","nein","50,6","57,1"),
(8192,12,"2,5526","2,6468","1,037","ja","19,5","23,4"),(8192,24,"1,9860","2,1558","1,085","nein","37,6","28,4"),(8192,48,"1,8788","1,8775","0,999","ja","50,8","47,8")]
for N,P,ps,pb,pr,pov,ks,kb in e4:
    rs=strip(P,N); zs=col(rs,'zeit_s',P=P,N=N); ks_=col(rs,'komm_max_s',P=P,N=N); zb=col(E4[P],'zeit_s',P=P,N=N); kb_=col(E4[P],'komm_max_s',P=P,N=N)
    assert len(zs)==len(zb)==20,(N,P,len(zs),len(zb))
    chk(f"E4 {N},{P} Streifen",ps,med(zs)); chk(f"E4 {N},{P} Blöcke",pb,med(zb)); chk(f"E4 {N},{P} B/S",pr,med(zb)/med(zs))
    if jn(ci_overlap(zs,zb))!=pov: ERR.append((f"E4 {N},{P} CI-Überlapp",pov,jn(ci_overlap(zs,zb))))
    else: N_OK[0]+=1
    chk_any(f"E4 {N},{P} Komm% S",ks,kp:= {"Med(k)/Med(z)":med(ks_)/med(zs)*100,"Med(k/z)":float(np.median(ks_/zs))*100}); chk_any(f"E4 {N},{P} Komm% B",kb,{"Med(k)/Med(z)":med(kb_)/med(zb)*100,"Med(k/z)":float(np.median(kb_/zb))*100})
print("   [Info] Komm%-Def.:",DEFCOUNT); DEFCOUNT.clear()
chk("E4 Raster-Rechnung 2*(256+341)","1194",2*(256+341))
report("E4 (Zeilen 269-275)")
# --- E5
E5={P:load(f"e5_overlap_P{P}_2026-11-01.csv") for P in (12,24,48)}
e5=[(48,256,"0,0521","0,0326","0,626","nein"),(48,512,"0,0664","0,0390","0,586","nein"),(48,1024,"0,0842","0,0495","0,588","nein"),(48,2048,"0,1385","0,0679","0,490","nein"),(48,4096,"0,4576","0,4502","0,984","nein"),(48,8192,"1,8788","1,8427","0,981","nein"),
(24,2048,"0,1601","0,0799","0,499","nein"),(24,4096,"0,5160","0,4845","0,939","nein"),(24,8192,"1,9860","2,0230","1,019","ja"),(12,2048,"0,2106","0,1318","0,626","nein"),(12,4096,"0,7151","0,5932","0,830","nein"),(12,8192,"2,5526","3,2266","1,264","ja")]
for P,N,ps,pu,pr,pov in e5:
    zs=col(strip(P,N),'zeit_s',P=P,N=N); zu=col(E5[P],'zeit_s',P=P,N=N); assert len(zs)==len(zu)==20
    chk(f"E5 {P},{N} S",ps,med(zs)); chk(f"E5 {P},{N} U",pu,med(zu)); chk(f"E5 {P},{N} U/S",pr,med(zu)/med(zs))
    if jn(ci_overlap(zs,zu))!=pov: ERR.append((f"E5 {P},{N} CI-Überlapp",pov,jn(ci_overlap(zs,zu))))
    else: N_OK[0]+=1
chk("E5 P=48 N=256 37 % weniger (1-0,626)","37",(1-med(col(E5[48],'zeit_s',P=48,N=256))/med(col(E1,'zeit_s',P=48,N=256)))*100)
chk("E5 P=48 N=2048 51 % weniger","51",(1-med(col(E5[48],'zeit_s',P=48,N=2048))/med(col(E1,'zeit_s',P=48,N=2048)))*100)
chk("E5 P=24 N=2048 50 %","50",(1-med(col(E5[24],'zeit_s',P=24,N=2048))/med(col(strip(24,2048),'zeit_s',P=24,N=2048)))*100)
ku=col(E5[48],'komm_max_s',P=48,N=8192); zu=col(E5[48],'zeit_s',P=48,N=8192)
chk_any("E5 Komm% Überlappung N=8192 P=48 24,2","24,2",{"Med(k)/Med(z)":med(ku)/med(zu)*100,"Med(k/z)":float(np.median(ku/zu))*100})
report("E5 (Zeilen 280-285)")
# --- E5b
E5b={P:load(f"e5b_nb_P{P}_2026-11-01.csv") for P in (12,24,48)}; print("E5b Zeilen",[len(E5b[P]) for P in E5b])
e5b=[(48,256,"0,0521","0,0328","0,0326","0,630","nein","0,994","ja"),(48,512,"0,0664","0,0412","0,0390","0,619","nein","0,947","ja"),(48,1024,"0,0842","0,0552","0,0495","0,655","nein","0,897","nein"),(48,2048,"0,1385","0,0996","0,0679","0,719","nein","0,682","nein"),(48,4096,"0,4576","0,4482","0,4502","0,979","nein","1,004","ja"),(48,8192,"1,8788","1,8184","1,8427","0,968","nein","1,013","nein"),
(24,2048,"0,1601","0,1111","0,0799","0,694","nein","0,719","nein"),(24,4096,"0,5160","0,4837","0,4845","0,937","nein","1,002","ja"),(24,8192,"1,9860","1,9219","2,0230","0,968","ja","1,053","ja"),
(12,2048,"0,2106","0,1740","0,1318","0,826","nein","0,758","nein"),(12,4096,"0,7151","0,6261","0,5932","0,876","nein","0,948","nein"),(12,8192,"2,5526","3,2525","3,2266","1,274","ja","0,992","ja")]
for P,N,ps,pn,pu,r1,o1,r2,o2 in e5b:
    zs=col(strip(P,N),'zeit_s',P=P,N=N); zn=col(E5b[P],'zeit_s',P=P,N=N); zu=col(E5[P],'zeit_s',P=P,N=N); assert len(zn)==20
    chk(f"E5b {P},{N} S",ps,med(zs)); chk(f"E5b {P},{N} NB",pn,med(zn)); chk(f"E5b {P},{N} U",pu,med(zu)); chk(f"E5b {P},{N} NB/S",r1,med(zn)/med(zs)); chk(f"E5b {P},{N} U/NB",r2,med(zu)/med(zn))
    for lab,a,b,pov in [("NBvsS",zn,zs,o1),("UvsNB",zu,zn,o2)]:
        if jn(ci_overlap(a,b))!=pov: ERR.append((f"E5b {P},{N} CI {lab}",pov,jn(ci_overlap(a,b))))
        else: N_OK[0]+=1
chk("E5b 0,490 = 0,719 × 0,682","0,490",0.719*0.682); chk("E5b ≈32 % weniger als NB (1-0,682)","32",(1-0.682)*100)
report("E5b (Zeilen 290-294)")
