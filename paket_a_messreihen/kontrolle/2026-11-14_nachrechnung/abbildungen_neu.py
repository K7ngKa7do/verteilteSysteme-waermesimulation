"""Neue Abbildungen fuer den Arbeitsbericht (Klaerungsphase 14.11.2026).

Farben: dataviz-Referenzpalette (validiert), Text in Texttoenen, eine Achse je Diagramm.
Aufruf (NumPy und Matplotlib):
    python3 abbildungen_neu.py AUSGABEORDNER e8_erg.npy
e8_erg.npy kommt aus e8_nachrechnung.py. Die Messwerte der Klaerungsphase stehen direkt im Skript
(nur Bildschirmausgaben, siehe Arbeitsbericht Anhang A.4). Erzeugt die neun Grafiken *_2026-11-14.png
(Arbeitsbericht Abb. 5, 6, 7, 13, 19, 21, 23, 29, 31)."""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, NullFormatter

OUT = sys.argv[1]
E8 = np.load(sys.argv[2], allow_pickle=True).item()
BLAU, ORANGE, AQUA, GELB = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TEXT, TEXT2, RASTER, GRAU = "#0b0b0b", "#52514e", "#e4e3df", "#a3a29c"
plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11, "axes.edgecolor": GRAU,
    "axes.labelcolor": TEXT, "xtick.color": TEXT2, "ytick.color": TEXT2, "text.color": TEXT,
    "axes.grid": True, "grid.color": RASTER, "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 150, "savefig.dpi": 150,
    "lines.linewidth": 2.0, "lines.markersize": 7, "axes.axisbelow": True})
komma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def k(x, n=2):
    return f"{x:.{n}f}".replace(".", ",")


def fertig(fig, name, fuss):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    y0 = min(a.get_tightbbox(r).transformed(fig.transFigure.inverted()).y0 for a in fig.axes)
    fig.text(0.01, y0 - 0.02, fuss, fontsize=8.5, color=TEXT2, ha="left", va="top")
    fig.savefig(f"{OUT}/{name}", facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("gespeichert:", name)


# 1) B1 Ueberbelegung: aktives Warten gegen CPU abgeben
y0 = [1.4647, 1.6749, 1.9477, 1.9469, 1.6620, 1.2973, 1.3460, 1.2740, 1.6139, 1.3497]
y1 = [0.1652, 0.1633, 0.1503, 0.1571, 0.1518, 0.1599, 0.1635, 0.1610, 0.1435, 0.1744]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
rng = np.random.default_rng(1)
for x, ys, c, lab in ((0, y0, ORANGE, "aktives Warten (Standard, yield=0)"), (1, y1, BLAU, "CPU abgeben (yield=1)")):
    ax.scatter(x + rng.uniform(-.12, .12, len(ys)), ys, color=c, s=46, edgecolor="white", linewidth=1, zorder=3, label=lab)
    m = float(np.median(ys))
    ax.plot([x - .25, x + .25], [m, m], color=TEXT, lw=1.6, zorder=4)
    ax.text(x + .3, m, f"Median {k(m, 4)} s", va="center", fontsize=10)
ax.axhline(0.1489, color=TEXT2, ls=(0, (4, 3)), lw=1.2)
ax.text(-0.55, 0.1489 * 0.87, "P=48 ohne Überbelegung (E16b): 0,1489 s", fontsize=9, color=TEXT2, ha="left", va="top")
ax.set_yscale("log"); ax.set_ylim(0.1, 3); ax.yaxis.set_major_formatter(komma); ax.yaxis.set_minor_formatter(NullFormatter())
ax.set_yticks([0.1, 0.2, 0.5, 1, 2])
ax.set_xticks([0, 1], ["mpi_yield_when_idle 0", "mpi_yield_when_idle 1"]); ax.set_xlim(-.6, 1.6)
ax.set_ylabel("Laufzeit [s] (200 Schritte)")
ax.set_title("B1: Überbelegung P=144 (36 je Rechner), N=2048 – Faktor 9,6 durch aktives Warten", loc="left")
ax.legend(loc="upper right", fontsize=9.5)
fertig(fig, "b1_ueberbelegung_yield_2026-11-14.png", "Je 10 Läufe abwechselnd, 14.11.2026, Bildschirmausgabe (keine CSV). Mann-Whitney exakt p ≈ 1,1·10⁻⁵.")

# 2) B3 Allreduce mit festem Algorithmus
Ps = [8, 12, 24, 48]
std = [19.42, 44.90, 40.75, 38.53]
rd = [57.68, 73.75, 136.74, 269.82]
ring = [18.48, 20.15, 13.25, 13.62]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
x = np.arange(4)
for ys, c, lab in ((std, BLAU, "Standard (Open MPI wählt selbst)"), (rd, ORANGE, "fest: recursive doubling"), (ring, AQUA, "fest: ring")):
    ax.plot(x, ys, color=c, marker="o", markeredgecolor="white", label=lab)
    ax.text(3.12, ys[-1] * (1.15 if c == AQUA else 1.0), k(ys[-1], 1) + " ms", va="center", fontsize=9.5, color=TEXT)
ax.plot([3], [90.37], marker="o", mfc="none", mec=BLAU, ms=8, ls="none")
ax.annotate("B3-Wert 90,4 ms (erhöht,\nnicht reproduziert; B3b: 38,5)", (3, 90.37), (1.9, 58), fontsize=8.5, color=TEXT2,
            arrowprops=dict(arrowstyle="-", color=GRAU, lw=1))
ax.axhline(13.4, color=TEXT2, ls=(0, (1, 2)), lw=1.2)
ax.text(0, 11.2, "Modell Ring bei P=48: 2·47/48·800 KB ÷ 117 MB/s ≈ 13,4 ms", fontsize=8.5, color=TEXT2)
ax.set_yscale("log"); ax.set_ylim(8, 400); ax.yaxis.set_major_formatter(komma); ax.yaxis.set_minor_formatter(NullFormatter())
ax.set_yticks([10, 20, 50, 100, 200])
ax.set_xticks(x, [f"P={p}\n({p // 4} je Rechner)" for p in Ps]); ax.set_xlim(-.3, 3.8)
ax.set_ylabel("Zeit je Allreduce [ms] (m = 800 KB)")
ax.set_title("B3: Allreduce über 4 Rechner – Algorithmus festgelegt", loc="left")
ax.legend(loc="upper left", fontsize=9.5)
fertig(fig, "b3_allreduce_algorithmus_2026-11-14.png", "Median aus 3 Durchgängen (Standard P=48: 10 Läufe, B3b), 100 Aufrufe je Lauf, ppr, 14.11.2026, Bildschirmausgabe.")

# 3) B4 Ping-Pong im Rechner mit/ohne CMA
groesse = [8, 4096, 32768, 262144, 1048576, 4194304, 16777216]
cma = [4, 711, 3212, 5594, 6855, 8445, 7521]
none = [5, 1082, 3902, 7649, 9407, 10047, 8650]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.plot(groesse, cma, color=BLAU, marker="o", markeredgecolor="white", label="CMA (Standard): Kernel kopiert direkt")
ax.plot(groesse, none, color=ORANGE, marker="o", markeredgecolor="white", label="ohne CMA: Kopie über gemeinsamen Puffer")
ax.set_xscale("log"); ax.set_xticks(groesse, ["8 B", "4 KiB", "32 KiB", "256 KiB", "1 MiB", "4 MiB", "16 MiB"])
ax.xaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
ax.set_ylabel("Datenrate [MB/s] (eine Richtung)"); ax.set_xlabel("Nachrichtengröße")
ax.set_title("B4: MPI im Rechner (2 Prozesse, manager) – ohne CMA 16–37 % schneller", loc="left")
ax.legend(loc="upper left", fontsize=9.5)
fertig(fig, "b4_pingpong_cma_2026-11-14.png", "Median aus 20 Versuchen je Größe, 14.11.2026, Bildschirmausgabe. C4: mit CMA ≈ 1,8 s Kernzeit (sys), ohne ≈ 0,13 s.")

# 4) B6 Cache-Effekt: Rate je Rechner gegen Datenmenge
mb = [16.8, 27.0, 33.5, 41.0, 67.1, 134.2]
rate = [6.57, 5.42, 3.19, 2.27, 1.89, 1.84]
Ns = [1024, 1300, 1448, 1600, 2048, 2896]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.plot(mb, rate, color=BLAU, marker="o", markeredgecolor="white", label="1 Rechner, 12 Prozesse")
for m_, r_, n_ in zip(mb, rate, Ns):
    ax.text(m_ * 1.04, r_ + 0.18, f"N={n_}", fontsize=8.5, color=TEXT2)
ax.plot([33.5], [2.39], marker="s", color=ORANGE, ls="none", ms=8, markeredgecolor="white",
        label="2 Rechner (P=24, N=2048), je Rechner")
ax.axvline(31.5, color=TEXT2, ls=(0, (4, 3)), lw=1.2)
ax.text(30.5, 0.35, "L3-Cache 30 MiB ≈ 31,5 MB", fontsize=9, color=TEXT2, ha="right")
ax.axhspan(1.84, 1.89, color=RASTER, zorder=0)
ax.text(140, 1.55, "Grenze Speicherbandbreite\n≈ 1,85–1,89 Mrd./s", fontsize=9, color=TEXT2, ha="right", va="top")
ax.set_xscale("log"); ax.set_xticks([16, 32, 64, 128], ["16", "32", "64", "128"]); ax.xaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_major_formatter(komma); ax.set_ylim(0, 7.5)
ax.set_xlabel("Daten je Rechner [MB] (2 Felder × N² × 8 B)"); ax.set_ylabel("Mrd. Updates/s je Rechner")
ax.set_title("B6: Rechenrate eines Rechners fällt an der L3-Grenze um Faktor 3,5", loc="left")
ax.legend(loc="center right", fontsize=9.5)
fertig(fig, "b6_cache_rate_2026-11-14.png", "Median aus 5 Durchgängen, 200 Schritte, Rate = (N−2)²·200 ÷ Zeit (Regel 1), 14.11.2026, Bildschirmausgabe.")

# 5) B7b-d Versatz von v gegen u
lab = ["0", "64 B", "2 KiB", "4 KiB", "16 KiB", "32 KiB", "64 KiB", "128 KiB", "256 KiB", "512 KiB", "1 MiB"]
einzel = {0: [2.2104, 2.2099, 2.2054], 1: [2.0936, 2.0926, 2.0908], 2: [1.3674, 1.3655, 1.3676],
          6: [1.3355, 1.3381, 1.3360], 7: [1.3684, 1.3707, 1.3713], 8: [1.3686, 1.3674, 1.3674], 9: [1.3619, 1.3686, 1.3634]}
b7b = {0: (2.2062, 2.2035, 2.2122), 3: (1.3691, 1.3668, 1.3762), 4: (1.3686, 1.3659, 1.3796), 5: (1.3571, 1.3547, 1.3603),
       10: (2.1961, 2.1931, 2.2055)}
fig, ax = plt.subplots(figsize=(8.2, 4.6))
langsam = lambda y: y > 1.6
for i, ys in einzel.items():
    for y in ys:
        ax.plot(i + 0.12, y, "o", color=ORANGE if langsam(y) else BLAU, ms=6, mec="white")
for i, (m, lo, hi) in b7b.items():
    c = ORANGE if langsam(m) else BLAU
    ax.errorbar(i - 0.12, m, yerr=[[m - lo], [hi - m]], fmt="D", color=c, ms=6, mec="white", capsize=3, lw=1.4)
ax.plot([], [], "D", color=TEXT2, ms=6, label="B7b: Median (Min–Max) aus 6 Läufen")
ax.plot([], [], "o", color=TEXT2, ms=6, label="B7c/B7d: Einzelläufe")
ax.text(0.5, 2.28, "langsam (orange)", color=ORANGE, fontsize=10)
ax.text(4.3, 1.45, "schnell (blau)", color=BLAU, fontsize=10)
ax.set_xticks(range(11), lab, rotation=0, fontsize=9); ax.set_ylim(1.2, 2.45)
ax.yaxis.set_major_formatter(komma)
ax.set_xlabel("Versatz von v gegenüber u innerhalb der 2-MiB-Seite (OFF)"); ax.set_ylabel("Laufzeit [s] (N=2048, P=1)")
ax.set_title("B7b–d: Der Versatz zwischen u und v legt den Zustand fest (51 Läufe)", loc="left")
ax.legend(loc="center right", fontsize=9)
fertig(fig, "b7_versatz_2026-11-14.png", "heat_versatz.py, große Seiten aktiv, manager, 14.11.2026, Bildschirmausgabe. Langsam: Abstand < 2 KiB (bezogen auf 1 MiB).")

# 6) B8 Hybrid: warum 4x12 langsamer ist
fig, ax = plt.subplots(figsize=(7.5, 4.6))
namen = ["4 × 12\n1 Rang\nje Rechner", "16 × 3\n4 Ränge\nje Rechner", "48 × 1\nparalleler Kern,\n1 Thread", "48 Ränge\nserieller Kern\n(B10)"]
werte = [0.6711, 0.4662, 0.4584, 0.4572]
ax.bar(range(4), werte, color=BLAU, width=0.6, edgecolor="white", linewidth=2)
for i, w in enumerate(werte):
    ax.text(i, w + 0.012, k(w, 4) + " s", ha="center", fontsize=10)
ax.axhline(0.443, color=ORANGE, ls=(0, (4, 3)), lw=1.6, label="Vorhersage Speicherbandbreite (B6): 0,443 s")
ax.annotate("Rechnen 0,44 s, danach\nAustausch ≈ 0,2 s – nacheinander", (0, 0.58), (0.45, 0.6), fontsize=9, color=TEXT2,
            arrowprops=dict(arrowstyle="-", color=GRAU, lw=1))
ax.legend(loc="upper right", fontsize=9)
ax.grid(axis="x", visible=False); ax.set_xticks(range(4), namen, fontsize=9); ax.set_ylim(0, 0.8); ax.yaxis.set_major_formatter(komma)
ax.set_ylabel("Laufzeit [s] (N=4096, 200 Schritte)")
ax.set_title("B8: Hybrid MPI + Threads – Nachteil entsteht durch Nacheinander", loc="left")
fertig(fig, "b8_hybrid_2026-11-14.png", "Median aus 3 Durchgängen, immer 48 Kerne, --bind-to none, 14.11.2026, Bildschirmausgabe.")

# 7) B9b Bytes je Update
fig, ax = plt.subplots(figsize=(6.8, 4.6))
lesen, schreiben = [16.897, 21.276], [8.073, 8.068]  # exakt aus den CAS-Rohwerten
x = np.arange(2)
ax.bar(x, lesen, width=0.5, color=BLAU, edgecolor="white", linewidth=2, label="gelesen")
ax.bar(x, schreiben, width=0.5, bottom=lesen, color=ORANGE, edgecolor="white", linewidth=2, label="geschrieben")
for i, (a, b) in enumerate(zip(lesen, schreiben)):
    ax.text(i, a + b + 0.8, k(a + b, 1) + " B", ha="center", fontsize=11)
for y, t in ((24, "24 B: Layer Condition\nerfüllt (Stengel et al. 2015)"), (40, "40 B: Layer Condition\nvoll verletzt")):
    ax.axhline(y, color=TEXT2, ls=(0, (1, 2)), lw=1.2)
    ax.text(1.38, y + 0.6, t, fontsize=8.5, color=TEXT2, ha="left", va="bottom")
ax.grid(axis="x", visible=False); ax.set_xticks(x, ["N = 32768\n(3 Zeilen = 0,75 MiB)", "N = 65536\n(3 Zeilen = 1,5 MiB)"]); ax.set_xlim(-.6, 2.6)
ax.set_ylim(0, 50); ax.set_ylabel("Bytes aus dem Arbeitsspeicher je Update")
ax.set_title("B9b: Speicherverkehr je Update (Zähler des Speichercontrollers)", loc="left")
ax.legend(loc="upper left", fontsize=9.5, ncol=2)
fertig(fig, "b9b_bytes_je_update_2026-11-14.png", "perf (unc_m_cas_count), manager, Differenz 30 − 10 Schritte, P=48, 14.11.2026. L3-Anteil je Kern ≈ 2,5 MiB.")

# 8) E8 Fehler gegen Gitterweite, mit und ohne Eckbereich
Ns8 = [17, 33, 65, 129]
h = np.array([1 / (n - 1) for n in Ns8])
fig, ax = plt.subplots(figsize=(7.5, 4.8))
reihen = [("rms_alle", BLAU, "RMS alle inneren Punkte", "Ordnung 1"),
          ("rms_o025", ORANGE, "RMS ohne Eckbereich (d < 0,25)", "Ordnung 2"),
          ("max_kern", AQUA, "Maximum im Kern [0,25; 0,75]²", "Ordnung 2")]
for key, c, lab_, ordn in reihen:
    y = [E8[n][key] for n in Ns8]
    ax.plot(h, y, color=c, marker="o", markeredgecolor="white", label=lab_)
    va = {"rms_alle": "center", "rms_o025": "top", "max_kern": "bottom"}[key]
    ax.text(h[-1] * 0.9, y[-1], ordn, ha="right", va=va, fontsize=9, color=TEXT)
ye = [E8[n]["max_ecke"] for n in Ns8[1:]]
ax.plot(h[1:], ye, color=GELB, marker="o", markeredgecolor="white", label="Maximum nahe heißer Ecke (d < 0,1)")
ax.text(h[2], ye[1] * 0.72, "≈ 0,718 – sinkt nicht", fontsize=9, color=TEXT, ha="center", va="top")
ax.set_xlim(1 / 300, 1 / 13)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xticks(h, ["1/16", "1/32", "1/64", "1/128"]); ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xlabel("Gitterweite h (N = 17, 33, 65, 129)"); ax.set_ylabel("Fehler gegen analytische Lösung")
ax.set_title("E8: Ordnung 2 abseits der Ecken, konstanter Fehler an den Sprungecken", loc="left")
ax.legend(loc="lower right", fontsize=9)
fertig(fig, "e8_ecken_2026-11-14.png", "Nachrechnung numpy (14.11.2026), r=0,2, praktisch stationär, Reihe mit 1001 Termen. N=17 ohne Eckwert (nur Diagonalpunkte).")

# 9) E9 Roofline-Vergleich: Stencil-Verkehr (25 B/Update) gegen Kopierrate
konf = ["P=1", "P=4", "P=8", "P=12", "P=4", "P=8", "P=12", "P=24", "P=48"]
kopie = [13.27, 39.71, 48.04, 46.84, 52.68, 92.04, 126.59, 181.88, 185.30]
upd = [0.619, 1.662, 1.848, 1.825, 2.175, 3.987, 5.256, 6.755, 7.140]
stencil = [u * 25 for u in upd]
fig, ax = plt.subplots(figsize=(8.6, 4.8))
x = np.array([0, 1, 2, 3, 4.7, 5.7, 6.7, 7.7, 8.7])
ax.bar(x - 0.2, kopie, width=0.38, color=BLAU, edgecolor="white", linewidth=2, label="Kopierrate (E10, STREAM-Zählung 16 B)")
ax.bar(x + 0.2, stencil, width=0.38, color=ORANGE, edgecolor="white", linewidth=2, label="Wärmekern: Updates/s × 25 B (B9b)")
for xi, a, b in zip(x, kopie, stencil):
    ax.text(xi, max(a, b) + 3, f"{100 * b / a:.0f} %", ha="center", fontsize=9)
ax.grid(axis="x", visible=False); ax.set_xticks(x, konf, fontsize=9)
ax.text(1.5, -32, "1 Rechner (slot)", ha="center", fontsize=10, color=TEXT2)
ax.text(6.7, -32, "4 Rechner (ppr, gleich viele je Rechner)", ha="center", fontsize=10, color=TEXT2)
ax.set_ylim(0, 205); ax.set_ylabel("GB/s"); ax.yaxis.set_major_formatter(komma)
ax.set_title("E9 (neu): Wärmekern gegen Kopierrate, N=8192", loc="left")
ax.legend(loc="upper left", fontsize=9)
fertig(fig, "e9_roofline_2026-11-14.png", "Volle Rechner (8–12 Prozesse): 96–97 %; bei 1–4 Prozessen je Rechner über 100 % → Kopierrate dort keine exakte Obergrenze.")
