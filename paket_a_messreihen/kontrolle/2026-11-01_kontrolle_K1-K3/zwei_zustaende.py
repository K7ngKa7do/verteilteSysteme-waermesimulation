# Kontrolle 01.11.2026: Zwei-Zustände-Prüfung der Serien mit breitem KI oder großer Lücke
# Eingabe: results/*.csv (Sicherung). Schwelle = Mitte der größten relativen Lücke zwischen sortierten Werten
# (post hoc gewählt, explorativ, kein statistischer Test).
import csv, os
import numpy as np
base = os.path.expanduser("~/mnt/waerme_sicherung_2026-11-01/results")
fall = [("e1_groesse",1,2048),("e2_node",12,4096),("e2_slot",4,4096),("e2b_node",2,2048),
        ("e2c_node",12,8192),("e2c_node",24,8192),("e2c_ppr_P12",12,8192),
        ("e4_bloecke_P12",12,8192),("e5_overlap_P12",12,8192),("e5b_nb_P12",12,8192)]
for name,P,N in fall:
    t = np.array([float(r["zeit_s"]) for r in csv.DictReader(open(f"{base}/{name}_2026-11-01.csv"))
                  if int(r["P"])==P and int(r["N"])==N])
    s = np.sort(t); k = np.argmax(s[1:]/s[:-1])+1; thr = (s[k]+s[k-1])/2
    sch, lang = t[t<=thr], t[t>thr]
    print(f"{name};P={P};N={N};n={len(t)};schwelle={thr:.3f};n_schnell={len(sch)};med_schnell={np.median(sch):.4f};"
          f"n_langsam={len(lang)};med_langsam={np.median(lang):.4f};faktor={np.median(lang)/np.median(sch):.2f};"
          f"anteil_langsam_%={100*len(lang)/len(t):.0f};median_gesamt={np.median(t):.4f}")
