"""Nachrechnung Teil 1: Baseline, Strong/Weak Scaling, E1, E2, E2b-d, E7, E9, E10, E11.

Zweck: Tabellenwerte des Arbeitsberichts Paket A aus den Roh-CSV neu rechnen und mit den Werten
im Bericht vergleichen (Arbeitsbericht, Anhang B.4). Zusammen mit pruefe_teil2.py: 663 Werte, 0 Abweichungen.
Aufruf (in diesem Ordner; Python 3 mit NumPy; klib2.py muss im selben Ordner liegen):
    python3 pruefe_teil1.py ../../03_Messdaten_Sicherung/Sicherung_Cluster_2026-11-14
Argument = Ordner der Cluster-Sicherung (enthaelt kadan/ und results/).
Ausgabe: je Bereich "geprueft / OK / Abweichungen" (gespeichert in pruefe_teil1_ausgabe.txt)."""
import sys

import numpy as np

import klib2 as K

K.D = sys.argv[1]
R = "results/"
P = K.Pruefer()

# ---------- Baseline ----------
b = K.gruppen(K.lies("kadan/baseline.csv"), "modus", "N")
soll = {("numba", "2048"): (1.3309, 1.3172, 1.3435, 629), ("numba", "4096"): (5.1694, 5.1251, 5.2254, 648),
        ("numpy", "2048"): (10.7618, 10.5780, 10.8477, 78)}
BASE = {}
for k, (m, lo, hi, mu) in soll.items():
    x = b[k]
    BASE[k] = K.med(x)
    P.gleich(f"Baseline {k} Median", K.med(x), m, 4)
    P.gleich(f"Baseline {k} KI lo", K.ki(x)[0], lo, 4)
    P.gleich(f"Baseline {k} KI hi", K.ki(x)[1], hi, 4)
    P.gleich(f"Baseline {k} Mio/s", K.ups(int(k[1]), 200, K.med(x)) / 1e6, mu, 0)
    assert len(x) == 20
P.gleich("NumPy/Numba N=2048", BASE[("numpy", "2048")] / BASE[("numba", "2048")], 8.1, 1)
P.bericht("Baseline")
B2048, B4096 = BASE[("numba", "2048")], BASE[("numba", "4096")]

# ---------- Strong Scaling 28.10. ----------
rows = K.lies(R + "a_strong_2026-10-28.csv")
g = K.gruppen(rows, "N", "P")
gk = K.gruppen(rows, "N", "P", wert="komm_max_s")
st = {
    "2048": {1: (2.2092, 2.1496, 2.2121, .0036, .60, 60.2), 2: (.7244, .7159, .7262, .0170, 1.84, 91.9),
             4: (.5034, .5007, .5144, .0291, 2.64, 66.1), 8: (.4577, .4533, .4620, .0394, 2.91, 36.4),
             12: (.4421, .4413, .4429, .0183, 3.01, 25.1), 24: (.1777, .1742, .1839, .1129, 7.49, 31.2),
             36: (.1561, .1450, .1588, .1188, 8.52, 23.7), 48: (.1409, .1367, .1453, .1129, 9.44, 19.7)},
    "4096": {1: (5.1909, 5.1857, 5.1949, .0040, 1.00, 99.6), 2: (2.8003, 2.7887, 2.8045, .0290, 1.85, 92.3),
             4: (2.5081, 1.9289, 2.5329, .8105, 2.06, 51.5), 8: (1.7799, 1.7656, 1.8004, .1136, 2.90, 36.3),
             12: (1.7953, 1.7757, 1.8212, .0789, 2.88, 24.0), 24: (.9063, .8866, .9207, .3441, 5.70, 23.8),
             36: (.5970, .5958, .5995, .2470, 8.66, 24.1), 48: (.4567, .4555, .4581, .2341, 11.32, 23.6)}}
KF_soll = {"4096": {2: .083, 4: .314, 8: .251, 12: .288, 24: .139, 36: .090, 48: .069},
           "2048": {2: .089, 4: .171, 8: .250, 12: .271, 24: .096, 36: .092, 48: .087}}
summen = {}
for N, tab in st.items():
    base = B2048 if N == "2048" else B4096
    for p, (m, lo, hi, km, S, E) in tab.items():
        x = g[(N, str(p))]
        assert len(x) == 20, (N, p, len(x))
        P.gleich(f"Strong N={N} P={p} Median", K.med(x), m, 4)
        P.gleich(f"Strong N={N} P={p} KI lo", K.ki(x)[0], lo, 4)
        P.gleich(f"Strong N={N} P={p} KI hi", K.ki(x)[1], hi, 4)
        P.gleich(f"Strong N={N} P={p} Komm-Median", K.med(gk[(N, str(p))]), km, 4)
        s = base / K.med(x)
        P.gleich(f"Strong N={N} P={p} Speedup(Baseline)", s, S, 2)
        P.gleich(f"Strong N={N} P={p} Effizienz", 100 * s / p, E, 1)
        if p > 1:
            P.gleich(f"Karp-Flatt N={N} P={p}", (1 / s - 1 / p) / (1 - 1 / p), KF_soll[N][p], 3)
    summen[N] = {r["summe"] for r in rows if r["N"] == N}
print("Strong: Pruefsummen je N:", {k: len(v) for k, v in summen.items()})
P.bericht("Strong Scaling 28.10. + Karp-Flatt")

# ---------- Weak Scaling 28.10. ----------
rows = K.lies(R + "a_weak_2026-10-28.csv")
g = K.gruppen(rows, "P", "N")
w = {("12", "4096"): (1.8174, 1.7869, 1.8455, 100.0, 1845), ("24", "5793"): (1.7652, 1.7560, 1.7807, 103.0, 3800),
     ("48", "8192"): (1.8200, 1.8156, 1.8237, 99.9, 7371)}
ref = K.med(g[("12", "4096")])
for k, (m, lo, hi, e, mu) in w.items():
    x = g[k]
    P.gleich(f"Weak {k} Median", K.med(x), m, 4)
    P.gleich(f"Weak {k} KI lo", K.ki(x)[0], lo, 4)
    P.gleich(f"Weak {k} KI hi", K.ki(x)[1], hi, 4)
    P.gleich(f"Weak {k} Effizienz", 100 * ref / K.med(x), e, 1)
    P.gleich(f"Weak {k} Mio/s", K.ups(int(k[1]), 200, K.med(x)) / 1e6, mu, 0)
P.bericht("Weak Scaling 28.10.")

# ---------- E1 ----------
rows = K.lies(R + "e1_groesse_2026-11-01.csv")
g = K.gruppen(rows, "N", "P")
gk = K.gruppen(rows, "N", "P", wert="komm_max_s")
e1 = {256: (.0134, .0050, 65.0, .0521, 97.4, 966), 512: (.0535, .0135, 51.5, .0664, 96.0, 973),
      1024: (.2230, .0320, 25.7, .0842, 91.4, 937), 2048: (2.2131, .4416, 4.1, .1385, 79.8, 378),
      4096: (5.1879, 1.7864, 4.3, .4576, 50.6, 646), 8192: (21.6662, 7.2347, 3.3, 1.8788, 50.8, 619)}
E1 = {}
for N, (m1, m12, k12, m48, k48, mu) in e1.items():
    t1, t12, t48 = (K.med(g[(str(N), p)]) for p in ("1", "12", "48"))
    E1[N] = (t1, t12, t48)
    P.gleich(f"E1 N={N} P1", t1, m1, 4)
    P.gleich(f"E1 N={N} P12", t12, m12, 4)
    P.gleich(f"E1 N={N} P48", t48, m48, 4)
    P.gleich(f"E1 N={N} Komm%12", 100 * K.med(gk[(str(N), "12")]) / t12, k12, 1)
    P.gleich(f"E1 N={N} Komm%48", 100 * K.med(gk[(str(N), "48")]) / t48, k48, 1)
    P.gleich(f"E1 N={N} Mio/s P1 (Regel 1)", K.ups(N, 200, t1) / 1e6, mu, 0)
sp12 = {256: 2.65, 512: 3.97, 1024: 6.97, 4096: 2.90, 8192: 2.99}
sp48 = {256: 0.26, 512: 0.80, 1024: 2.65, 4096: 11.34, 8192: 11.53}
for N in sp12:
    P.gleich(f"E1 N={N} S12", E1[N][0] / E1[N][1], sp12[N], 2)
    P.gleich(f"E1 N={N} S48", E1[N][0] / E1[N][2], sp48[N], 2)
P.gleich("E1 N=2048 S12 gg. Baseline", B2048 / E1[2048][1], 3.01, 2)
P.gleich("E1 N=2048 S48 gg. Baseline", B2048 / E1[2048][2], 9.61, 2)
P.bericht("E1 Gittergroesse")

# ---------- E2 ----------
gs = K.gruppen(K.lies(R + "e2_slot_2026-11-01.csv"), "N", "P")
gn = K.gruppen(K.lies(R + "e2_node_2026-11-01.csv"), "N", "P")
gsk = K.gruppen(K.lies(R + "e2_slot_2026-11-01.csv"), "N", "P", wert="komm_max_s")
gnk = K.gruppen(K.lies(R + "e2_node_2026-11-01.csv"), "N", "P", wert="komm_max_s")
e2 = {("2048", "4"): (.5048, .4973, .5135, .3850, .3747, .3939, 1.31, 5.3, 30.2),
      ("2048", "8"): (.4702, .4576, .4750, .2817, .2759, .2860, 1.67, 11.7, 47.1),
      ("2048", "12"): (.4419, .4410, .4431, .2624, .2575, .2674, 1.68, 4.1, 60.2),
      ("2048", "24"): (.1751, .1736, .1820, .3575, .3565, .3593, 0.49, 63.4, 85.4),
      ("4096", "4"): (2.5226, 1.9956, 2.5652, 2.3949, 2.3897, 2.4087, 1.05, 32.1, 44.6),
      ("4096", "8"): (1.7896, 1.7799, 1.7986, .9364, .9322, .9452, 1.91, 5.6, 25.3),
      ("4096", "12"): (1.8031, 1.7878, 1.8262, .7892, .7788, .8037, 2.28, 4.2, 35.3),
      ("4096", "24"): (.9088, .9000, .9208, .7235, .7034, .7486, 1.26, 42.5, 64.1)}
for k, (sm, slo, shi, nm, nlo, nhi, ratio, ks, kn) in e2.items():
    xs, xn = gs[k], gn[k]
    P.gleich(f"E2 {k} slot", K.med(xs), sm, 4)
    P.gleich(f"E2 {k} slot KIlo", K.ki(xs)[0], slo, 4)
    P.gleich(f"E2 {k} slot KIhi", K.ki(xs)[1], shi, 4)
    P.gleich(f"E2 {k} node", K.med(xn), nm, 4)
    P.gleich(f"E2 {k} node KIlo", K.ki(xn)[0], nlo, 4)
    P.gleich(f"E2 {k} node KIhi", K.ki(xn)[1], nhi, 4)
    P.gleich(f"E2 {k} slot/node", K.med(xs) / K.med(xn), ratio, 2)
    P.gleich(f"E2 {k} Komm% slot", 100 * K.med(gsk[k]) / K.med(xs), ks, 1)
    P.gleich(f"E2 {k} Komm% node", 100 * K.med(gnk[k]) / K.med(xn), kn, 1)
P.bericht("E2 slot/node")

# ---------- E2b (P=2, 36) und Reproduzierbarkeit ----------
gbs = K.gruppen(K.lies(R + "e2b_slot_2026-11-01.csv"), "N", "P")
gbn = K.gruppen(K.lies(R + "e2b_node_2026-11-01.csv"), "N", "P")
print("E2b Mediane slot/node:", {k: (round(K.med(gbs[k]), 4), round(K.med(gbn[k]), 4)) for k in sorted(gbs)})
strong = K.gruppen(K.lies(R + "a_strong_2026-10-28.csv"), "N", "P")
rep = {("2048", "2"): .2, ("2048", "4"): .3, ("2048", "8"): 2.7, ("2048", "12"): 0.0, ("2048", "24"): -1.5,
       ("2048", "36"): -.5, ("4096", "2"): -.2, ("4096", "4"): .6, ("4096", "8"): .5, ("4096", "12"): .4,
       ("4096", "24"): .3, ("4096", "36"): .3}
for k, v in rep.items():
    neu = K.med(gs[k]) if k in gs else K.med(gbs[k])
    P.gleich(f"Reprod. {k}", 100 * (neu / K.med(strong[k]) - 1), v, 1)
P.bericht("E2b + Reproduzierbarkeit 01.11. gg. 28.10.")

# ---------- E2d ppr ----------
gd = K.gruppen(K.lies(R + "e2d_ppr_2026-11-01.csv"), "N", "P")
e2d = {("4096", 8): (.8855, 5.84, 51.7), ("4096", 12): (.7151, 7.23, 64.0), ("4096", 24): (.5160, 10.02, 88.7),
       ("4096", 36): (.4654, 11.11, 98.3), ("2048", 8): (.2711, 4.91, 51.1), ("2048", 12): (.2106, 6.32, 65.8),
       ("2048", 24): (.1601, 8.31, 86.5), ("2048", 36): (.1460, 9.11, 94.8)}
E2D = {}
for (N, p), (m, S, anteil) in e2d.items():
    x = gd[(N, str(p))]
    base = B2048 if N == "2048" else B4096
    t48 = E1[int(N)][2]
    E2D[(int(N), p)] = K.med(x)
    P.gleich(f"E2d N={N} P={p} Median", K.med(x), m, 4)
    P.gleich(f"E2d N={N} P={p} Speedup", base / K.med(x), S, 2)
    P.gleich(f"E2d N={N} P={p} Anteil P48 (Regel 2)", 100 * t48 / K.med(x), anteil, 1)
P.gleich("E2d P48 N=2048 S (E1)", B2048 / E1[2048][2], 9.61, 2)
P.gleich("E2d P48 N=4096 S (E1)", B4096 / E1[4096][2], 11.30, 2)
P.gleich("E2d P48 N=4096 E (E1)", 100 * B4096 / E1[4096][2] / 48, 23.5, 1)
P.bericht("E2d ppr")

# ---------- E2c N=8192 ----------
e2c = {"slot": K.gruppen(K.lies(R + "e2c_slot_2026-11-01.csv"), "P"),
       "node": K.gruppen(K.lies(R + "e2c_node_2026-11-01.csv"), "P")}
pp = {}
for p in (4, 8, 12, 24):
    pp[str(p)] = [float(r["zeit_s"]) for r in K.lies(R + f"e2c_ppr_P{p}_2026-11-01.csv")]
e2c["ppr"] = pp
soll = {("slot", 4): (8.0718, 7.9786, 8.1281), ("node", 4): (6.1661, 6.1427, 6.2287), ("ppr", 4): (6.1691, 6.1493, 6.2248),
        ("slot", 8): (7.2597, 7.0720, 7.3184), ("node", 8): (3.5151, 3.4887, 3.5602), ("ppr", 8): (3.3648, 3.3479, 3.3956),
        ("slot", 12): (7.3506, 7.2966, 7.4821), ("node", 12): (3.3322, 2.9488, 5.1119), ("ppr", 12): (2.5526, 2.4995, 3.2855),
        ("slot", 24): (3.6896, 3.6752, 3.7081), ("node", 24): (2.6041, 2.5677, 7.9905), ("ppr", 24): (1.9860, 1.9600, 2.0573)}
E2C = {}
for (mp, p), (m, lo, hi) in soll.items():
    x = e2c[mp][(str(p),) if mp != "ppr" else str(p)]
    E2C[(mp, p)] = K.med(x)
    P.gleich(f"E2c {mp} P={p}", K.med(x), m, 4)
    P.gleich(f"E2c {mp} P={p} KIlo", K.ki(x)[0], lo, 4)
    P.gleich(f"E2c {mp} P={p} KIhi", K.ki(x)[1], hi, 4)
P.gleich("E2c ppr P24 / P48 (E1)", 100 * E1[8192][2] / E2C[("ppr", 24)], 94.6, 1)
P.bericht("E2c N=8192")

# ---------- E10 Bandbreite ----------
g10 = K.gruppen(K.lies(R + "e10_bandbreite_2026-11-01.csv"), "modus", "P", wert="gb_summe")
e10 = {("ein_rechner", 1): 13.27, ("ein_rechner", 2): 23.20, ("ein_rechner", 4): 39.71, ("ein_rechner", 6): 46.05,
       ("ein_rechner", 8): 48.04, ("ein_rechner", 12): 46.84, ("vier_rechner", 4): 52.68, ("vier_rechner", 8): 92.04,
       ("vier_rechner", 12): 126.59, ("vier_rechner", 24): 181.88, ("vier_rechner", 48): 185.30}
BW = {}
for (mo, p), v in e10.items():
    BW[(mo, p)] = K.med(g10[(mo, str(p))])
    P.gleich(f"E10 {mo} P={p}", BW[(mo, p)], v, 2)
P.gleich("E10 ein P8 KIlo", K.ki(g10[("ein_rechner", "8")])[0], 47.87, 2)
P.gleich("E10 vier P48 KIhi", K.ki(g10[("vier_rechner", "48")])[1], 185.77, 2)
P.bericht("E10 Speicherbandbreite")

# ---------- E9 neu (25 B je Update, Regel 1) ----------
print("E9 (N=8192, Regel 1, 25 B/Update):")
fall = [("slot P=1", E1[8192][0], BW[("ein_rechner", 1)]), ("slot P=4", E2C[("slot", 4)], BW[("ein_rechner", 4)]),
        ("slot P=8", E2C[("slot", 8)], BW[("ein_rechner", 8)]), ("slot P=12", E2C[("slot", 12)], BW[("ein_rechner", 12)]),
        ("ppr P=4", E2C[("ppr", 4)], BW[("vier_rechner", 4)]), ("ppr P=8", E2C[("ppr", 8)], BW[("vier_rechner", 8)]),
        ("ppr P=12", E2C[("ppr", 12)], BW[("vier_rechner", 12)]), ("ppr P=24", E2C[("ppr", 24)], BW[("vier_rechner", 24)]),
        ("ppr P=48", E1[8192][2], BW[("vier_rechner", 48)])]
for name, t, bw in fall:
    u = K.ups(8192, 200, t) / 1e9
    print(f"   {name}: {u:.3f} Mrd. Upd/s; x25 B = {u * 25:.1f} GB/s; Kopierrate {bw:.2f} GB/s; Anteil {100 * u * 25 / bw:.0f} %"
          f"; (alt 16 B: {100 * u * 16 / bw:.0f} %)")

# ---------- E7 Amdahl ----------
def fit(Ps, Ss):
    best = None
    for s in np.linspace(0, .5, 50001):
        f = sum((S - 1 / (s + (1 - s) / p)) ** 2 for p, S in zip(Ps, Ss))
        if best is None or f < best[1]:
            best = (s, f)
    return best[0]

for N, base, soll_s in ((2048, B2048, .0841), (4096, B4096, .0651)):
    Ps = [8, 12, 24, 36, 48]
    Ss = [base / E2D[(N, p)] for p in Ps[:-1]] + [base / E1[N][2]]
    s = fit(Ps, Ss)
    P.gleich(f"E7 N={N} s", s, soll_s, 4)
    print(f"E7 N={N}: s={s:.4f}, Smax={1 / s:.1f}, Abw. max {max(abs(S - 1 / (s + (1 - s) / p)) for p, S in zip(Ps, Ss)):.2f}")
Ps = [4, 8, 12, 24, 48]
Ss = [E1[8192][0] / E2C[("ppr", p)] for p in Ps[:-1]] + [E1[8192][0] / E1[8192][2]]
s = fit(Ps, Ss)
P.gleich("E7 N=8192 s", s, .0599, 4)
print(f"E7 N=8192: s={s:.4f}, Smax={1 / s:.1f}, Abw. max {max(abs(S - 1 / (s + (1 - s) / p)) for p, S in zip(Ps, Ss)):.2f}")
P.bericht("E7 Amdahl")
