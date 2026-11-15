"""Nachrechnung Teil 2: E3, E4, E5, E5b, E13-E13d, E14, E15 (vollstaendige Tabelle A.6), E16b, E18, E6.

Zweck und Aufruf wie pruefe_teil1.py:
    python3 pruefe_teil2.py ../../03_Messdaten_Sicherung/Sicherung_Cluster_2026-11-14
Ausgabe gespeichert in pruefe_teil2_ausgabe.txt. Hinweis: Die E15-Pruefung umfasst alle 32 Zeilen
der Tabelle in Anhang A.6 (Median und beide Grenzen des 95-%-Intervalls = 96 Werte); sie lief am
14.11. zunaechst als Einzelbefehl und wurde am 15.11. in dieses Skript uebernommen."""
import math
import sys

import numpy as np

import klib2 as K

K.D = sys.argv[1]
R = "results/"
P = K.Pruefer()

# ---------- E3 Ping-Pong ----------
rows = K.lies(R + "e3_pingpong_2026-11-01.csv")
g = K.gruppen(rows, "modus", "groesse_byte", wert="zeit_einfach_s")
e3 = {8: (1.80, 4.4, 53.10, 0.2), 64: (1.83, 35.0, 54.69, 1.2), 512: (2.37, 215.8, 66.66, 7.7),
      4096: (5.73, 715.2, 123.39, 33.2), 32768: (10.00, 3276.4, 376.06, 87.1), 262144: (46.81, 5599.6, 2442.98, 107.3),
      1048576: (152.32, 6884.2, 9114.20, 115.0), 4194304: (522.94, 8020.6, 35865.01, 116.9),
      16777216: (2191.64, 7655.1, 142789.72, 117.5)}
for n, (ti, bi, te, be) in e3.items():
    a, c = K.med(g[("intra", str(n))]), K.med(g[("inter", str(n))])
    P.gleich(f"E3 intra {n} us", a * 1e6, ti, 2)
    P.gleich(f"E3 intra {n} MB/s", n / a / 1e6, bi, 1)
    P.gleich(f"E3 inter {n} us", c * 1e6, te, 2)
    P.gleich(f"E3 inter {n} MB/s", n / c / 1e6, be, 1)
for mo, a_soll, b_soll in (("intra", 1.80, 7689), ("inter", 53.10, 118)):
    ns = [262144, 1048576, 4194304, 16777216]
    ts = [K.med(g[(mo, str(n))]) for n in ns]
    slope = np.polyfit(ns, ts, 1)[0]
    P.gleich(f"E3 {mo} alpha us", K.med(g[(mo, '8')]) * 1e6, a_soll, 2)
    P.gleich(f"E3 {mo} beta MB/s", 1 / slope / 1e6, b_soll, 0)
P.bericht("E3 Ping-Pong + Hockney")

# ---------- E4 Bloecke gegen Streifen ----------
blk = {}
for p in (12, 24, 48):
    for k, v in K.gruppen(K.lies(R + f"e4_bloecke_P{p}_2026-11-01.csv"), "N").items():
        blk[(int(k[0]), p)] = K.med(v)
e4 = {(2048, 12): .2044, (2048, 24): .1401, (2048, 48): .1180, (4096, 12): .7022, (4096, 24): .5894,
      (4096, 48): .4915, (8192, 12): 2.6468, (8192, 24): 2.1558, (8192, 48): 1.8775}
for k, v in e4.items():
    P.gleich(f"E4 Bloecke {k}", blk[k], v, 4)
P.bericht("E4 Bloecke")

# ---------- E5 / E5b ----------
for tag, datei, soll in (
        ("E5 Ueberlappung", "e5_overlap", {(48, 256): .0326, (48, 512): .0390, (48, 1024): .0495, (48, 2048): .0679,
                                           (48, 4096): .4502, (48, 8192): 1.8427, (24, 2048): .0799, (24, 4096): .4845,
                                           (24, 8192): 2.0230, (12, 2048): .1318, (12, 4096): .5932, (12, 8192): 3.2266}),
        ("E5b nicht blockierend", "e5b_nb", {(48, 256): .0328, (48, 512): .0412, (48, 1024): .0552, (48, 2048): .0996,
                                             (48, 4096): .4482, (48, 8192): 1.8184, (24, 2048): .1111, (24, 4096): .4837,
                                             (24, 8192): 1.9219, (12, 2048): .1740, (12, 4096): .6261, (12, 8192): 3.2525})):
    for (p, N), v in soll.items():
        x = K.gruppen(K.lies(R + f"{datei}_P{p}_2026-11-01.csv"), "N")[(str(N),)]
        P.gleich(f"{tag} P={p} N={N}", K.med(x), v, 4)
    P.bericht(tag)


# ---------- E13 Test A/B ----------
def zustaende(t, nref):
    t = np.asarray(t)
    ref = float(np.median(np.sort(t)[:nref]))
    lang = t > 1.15 * ref
    wechsel = int(np.sum(lang[1:] != lang[:-1]))
    p = lang.mean()
    erw = 2 * p * (1 - p) * (len(t) - 1)
    serien = {True: 0, False: 0}
    cur, n = lang[0], 1
    for x in lang[1:]:
        if x == cur:
            n += 1
        else:
            serien[bool(cur)] = max(serien[bool(cur)], n)
            cur, n = x, 1
    serien[bool(cur)] = max(serien[bool(cur)], n)
    return ref, lang, wechsel, erw, serien


for name, datei, soll in (("A", "e13_N2048_P1_2026-11-01.csv", (1.3017, 2.2070, 2.2241, 1.3259, 149, 2.2092, 1.3341, 74, 75.6, 14, 3)),
                          ("B", "e13_N4096_P4_2026-11-01.csv", (1.8876, 2.5161, 2.6311, 1.9180, 119, 2.5445, 1.9623, 93, 95.9, 11, 5))):
    t = [float(r["zeit_s"]) for r in K.lies(R + datei)]
    ref, lang, w, erw, ser = zustaende(t, 20)
    t = np.asarray(t)
    vals = (t.min(), K.med(t), t.max(), ref, int(lang.sum()), K.med(t[lang]), K.med(t[~lang]), w, erw, ser[True], ser[False])
    st = (4, 4, 4, 4, 0, 4, 4, 0, 1, 0, 0)
    for i, (a, b, s) in enumerate(zip(vals, soll, st)):
        P.gleich(f"E13 {name} Wert{i}", a, b, s)
    print(f"E13 {name}: n={len(t)}, Faktor langsam/schnell {K.med(t[lang]) / K.med(t[~lang]):.2f}, Anteil {100 * lang.mean():.1f} %")
P.bericht("E13 Test A/B")

# ---------- E13b ----------
rows = K.lies(R + "e13b_cpu_N2048_P1_2026-11-01.csv")
t = np.array([float(r["zeit_s"]) for r in rows])
ref, lang, *_ = zustaende(t, 20)
P.gleich("E13b langsam", int(lang.sum()), 140, 0)
P.gleich("E13b Referenz", ref, 1.3262, 4)
P.gleich("E13b Median alle", K.med(t), 2.2077, 4)
P.gleich("E13b Median langsam", K.med(t[lang]), 2.2100, 4)
cpu = np.array([r["cpu_start"] for r in rows])
P.gleich("E13b Kern0 Laeufe", int((cpu == "0").sum()), 193, 0)
P.gleich("E13b Kern0 langsam", int(lang[cpu == "0"].sum()), 135, 0)
P.gleich("E13b Kern1 langsam", int(lang[cpu == "1"].sum()), 5, 0)
P.bericht("E13b")

# ---------- E13c ----------
rows = K.lies(R + "e13c_kern_2026-11-09.csv")
t = np.array([float(r["zeit_s"]) for r in rows])
kern = np.array([r["kern"] for r in rows])
ref = float(np.median(np.sort(t)[:16]))
lang = t > 1.15 * ref
P.gleich("E13c Referenz", ref, 1.3155, 4)
for k, (n, m) in {"0": (31, 2.1957), "2": (27, 2.1994), "12": (26, 2.2287), "22": (25, 2.1928)}.items():
    P.gleich(f"E13c CPU{k} langsam", int(lang[kern == k].sum()), n, 0)
    P.gleich(f"E13c CPU{k} Median", K.med(t[kern == k]), m, 4)
obs = np.array([[lang[kern == k].sum(), (~lang[kern == k]).sum()] for k in ("0", "2", "12", "22")], dtype=float)
exp = obs.sum(1, keepdims=True) * obs.sum(0, keepdims=True) / obs.sum()
chi2 = float(((obs - exp) ** 2 / exp).sum())
pchi = math.erfc(math.sqrt(chi2 / 2)) + math.sqrt(2 * chi2 / math.pi) * math.exp(-chi2 / 2)  # df=3
P.gleich("E13c chi2", chi2, 2.39, 2)
P.gleich("E13c p", pchi, 0.50, 2)
P.gleich("E13c Fisher CPU0", K.fisher2(31, 9, 78, 42), 0.17, 2)
P.bericht("E13c")

# ---------- E13d ----------
rows = K.lies(R + "e13d_bloecke_2026-11-09.csv")
t = np.array([float(r["zeit_s"]) for r in rows])
bl = np.array([[float(r[f"b{i}"]) for i in range(1, 21)] for r in rows])
ref = float(np.median(np.sort(t)[:6]))
lang = t > 1.15 * ref
P.gleich("E13d Referenz", ref, 1.3488, 4)
P.gleich("E13d langsam", int(lang.sum()), 49, 0)
P.gleich("E13d Block schnell", K.med(bl[~lang].ravel()), .06751, 5)
P.gleich("E13d Block langsam", K.med(bl[lang].ravel()), .11156, 5)
mm = bl.max(1) / bl.min(1)
P.gleich("E13d max/min schnell", mm[~lang].max(), 1.043, 3)
P.gleich("E13d max/min langsam", mm[lang].max(), 1.135, 3)
P.bericht("E13d")

# ---------- E14 ----------
g = K.gruppen(K.lies(R + "e14_ghost_2026-11-09.csv"), "N", "g")
gk = K.gruppen(K.lies(R + "e14_ghost_2026-11-09.csv"), "N", "g", wert="komm_max_s")
e14 = {(256, 1): (.0526, .0515, .0537, 97), (256, 2): (.0331, .0325, .0335, 95), (256, 4): (.0205, .0203, .0224, 94),
       (512, 1): (.0668, .0649, .0707, 95), (512, 2): (.0409, .0398, .0427, 94), (512, 4): (.0308, .0295, .0338, 91),
       (1024, 1): (.0835, .0816, .0894, 91), (1024, 2): (.0633, .0608, .0706, 87), (1024, 4): (.0529, .0510, .0634, 84),
       (2048, 1): (.1368, .1326, .1427, 79), (2048, 2): (.1178, .1133, .1292, 75), (2048, 4): (.1355, .1336, .1391, 78)}
for (N, gg), (m, lo, hi, kp) in e14.items():
    x = g[(str(N), str(gg))]
    P.gleich(f"E14 N={N} g={gg}", K.med(x), m, 4)
    P.gleich(f"E14 N={N} g={gg} lo", K.ki(x)[0], lo, 4)
    P.gleich(f"E14 N={N} g={gg} hi", K.ki(x)[1], hi, 4)
    P.gleich(f"E14 N={N} g={gg} Komm%", 100 * K.med(gk[(str(N), str(gg))]) / K.med(x), kp, 0)
P.bericht("E14 Ghost-Zone")

# ---------- E15 (vollstaendige Tabelle, Arbeitsbericht Anhang A.6: Median und 95-%-KI in Mikrosekunden) ----------
rows15 = K.lies(R + "e15_allreduce_2026-11-09.csv")
g = K.gruppen(rows15, "m", "P", "map")
A6 = """1 1 slot 3,0 2,9 3,1
1 2 slot 5,3 5,2 5,4
1 4 slot 4,0 3,9 4,5
1 12 slot 9,6 5,9 10,2
1 8 ppr:2:node 137,8 134,6 142,1
1 12 ppr:3:node 227,2 224,0 230,9
1 24 ppr:6:node 242,3 236,6 247,5
1 48 ppr:12:node 271,0 265,0 273,4
1000 1 slot 3,4 3,3 3,5
1000 2 slot 10,3 10,2 10,5
1000 4 slot 17,6 17,3 18,3
1000 12 slot 49,1 41,1 56,2
1000 8 ppr:2:node 522,7 503,2 529,5
1000 12 ppr:3:node 673,2 654,6 678,2
1000 24 ppr:6:node 863,3 849,4 877,6
1000 48 ppr:12:node 822,9 803,6 828,1
100000 1 slot 58,8 58,3 59,2
100000 2 slot 226,5 223,5 228,2
100000 4 slot 371,0 349,5 382,9
100000 12 slot 825,4 814,6 873,4
100000 8 ppr:2:node 19608,5 19303,9 21180,8
100000 12 ppr:3:node 45662,8 44301,9 53587,7
100000 24 ppr:6:node 42575,0 40637,5 50114,2
100000 48 ppr:12:node 40259,9 38183,0 40501,7
1000000 1 slot 503,9 501,6 514,8
1000000 2 slot 2418,1 2406,4 2428,7
1000000 4 slot 5523,0 5425,1 5657,1
1000000 12 slot 21094,5 20624,1 21413,0
1000000 8 ppr:2:node 200379,8 198928,1 203358,2
1000000 12 ppr:3:node 436108,2 428368,3 476096,0
1000000 24 ppr:6:node 423025,9 411678,6 439559,7
1000000 48 ppr:12:node 400947,5 394307,8 404260,4"""
zahl = lambda t: float(t.replace(",", "."))
for zeile in A6.splitlines():
    m, Pn, mp, md, lo, hi = zeile.split()
    x = g[(m, Pn, mp)]
    P.gleich(f"E15 m={m} P={Pn} {mp} Median", K.med(x) * 1e6, zahl(md), 1)
    P.gleich(f"E15 m={m} P={Pn} {mp} KI unten", K.ki(x)[0] * 1e6, zahl(lo), 1)
    P.gleich(f"E15 m={m} P={Pn} {mp} KI oben", K.ki(x)[1] * 1e6, zahl(hi), 1)
falsch = sum(1 for r in rows15 if abs(float(r["ergebnis"]) - float(r["P"])) > 1e-9)
print("E15 Gruppen:", len(g), "(erwartet 32) | je Gruppe n:", sorted({len(v) for v in g.values()}),
      "| falsche Allreduce-Ergebnisse:", falsch)
P.bericht("E15 Allreduce (vollstaendige Tabelle A.6)")

# ---------- E16b ----------
g = K.gruppen(K.lies(R + "e16b_ueberbelegung_2026-11-09.csv"), "P")
for p, (m, lo, hi) in {"48": (.1489, .1342, .1593), "96": (.1418, .1369, .1511), "144": (1.4193, 1.3114, 1.5443),
                       "192": (2.1035, 1.9965, 2.1949)}.items():
    x = g[(p,)]
    P.gleich(f"E16b P={p}", K.med(x), m, 4)
    P.gleich(f"E16b P={p} lo", K.ki(x)[0], lo, 4)
    P.gleich(f"E16b P={p} hi", K.ki(x)[1], hi, 4)
P.gleich("E16b P48 max", max(g[("48",)]), .4515, 4)
P.bericht("E16b Ueberbelegung")

# ---------- E18 ----------
rows = K.lies(R + "e18_thp_aus_2026-11-09.csv")
g = K.gruppen(rows, "N", "P", "thp")
e18 = {("2048", "1", "0"): (1.3395, 0), ("2048", "1", "1"): (2.2093, 16), ("2048", "2", "0"): (.7202, 0),
       ("2048", "2", "1"): (.7228, 0), ("2048", "4", "0"): (.4917, 0), ("2048", "4", "1"): (.4997, 1),
       ("4096", "1", "0"): (5.3347, 0), ("4096", "1", "1"): (5.1913, 0), ("4096", "2", "0"): (2.8362, 0),
       ("4096", "2", "1"): (2.8090, 0), ("4096", "4", "0"): (1.9172, 0), ("4096", "4", "1"): (2.5071, 13)}
for k, (m, nl) in e18.items():
    x = np.array(g[k])
    ref = K.med(g[(k[0], k[1], "0")])
    P.gleich(f"E18 {k}", K.med(x), m, 4)
    P.gleich(f"E18 {k} langsam", int((x > 1.15 * ref).sum()), nl, 0)
P.gleich("E18 Fisher 2048/1", K.fisher2(16, 4, 0, 20) * 1e7, 1.5, 1)
P.gleich("E18 Fisher 4096/4", K.fisher2(13, 7, 0, 20) * 1e5, 1.3, 1)
P.bericht("E18 grosse Seiten")

# ---------- E6 ----------
g = K.gruppen(K.lies(R + "e6_hybrid_2026-11-09.csv"), "N", "P", "T")
e6 = {("2048", "48", "1"): .1431, ("2048", "24", "2"): .1505, ("2048", "12", "4"): .1345, ("2048", "8", "6"): .1462,
      ("2048", "4", "12"): .1598, ("4096", "48", "1"): .4577, ("4096", "24", "2"): .4689, ("4096", "12", "4"): .4872,
      ("4096", "8", "6"): .4959, ("4096", "4", "12"): .6440}
for k, v in e6.items():
    P.gleich(f"E6 {k}", K.med(g[k]), v, 4)
P.bericht("E6 Hybrid")
