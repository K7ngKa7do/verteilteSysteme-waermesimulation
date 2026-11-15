"""E8 nachgerechnet: FTCS r=0,2 bis praktisch stationaer gegen Reihenloesung (Laplace im Quadrat).
Rand: Zeile 0 (y=0) = 100, sonst 0 - wie heat_csv.py. Ausgabe: Fehlermasse je N (inkl. Ecken-Auswertung).

Aufruf (nur NumPy, keine Clusterdaten; Laufzeit wenige Sekunden):
    python3 e8_nachrechnung.py e8_erg.npy
Schreibt die Ergebnisse nach e8_erg.npy (Eingabe fuer abbildungen_neu.py) und gibt die Fehlermasse aus
(gespeichert in e8_nachrechnung_ausgabe.txt). Arbeitsbericht Kapitel 6.15."""
import math
import sys

import numpy as np

r = 0.2


def ftcs(N):
    h = 1.0 / (N - 1)
    steps = int(14 / (r * 2 * math.pi ** 2 * h * h))
    u = np.zeros((N, N))
    u[0, :] = 100.0
    v = u.copy()
    for _ in range(steps):
        v[1:-1, 1:-1] = u[1:-1, 1:-1] + r * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] - 4 * u[1:-1, 1:-1])
        u, v = v, u
    return u, steps


def analytisch(N, terme=1001):
    h = 1.0 / (N - 1)
    y = np.arange(N)[:, None] * h  # Zeile i <-> y = i*h (Zeile 0 = heisser Rand)
    x = np.arange(N)[None, :] * h
    s = np.zeros((N, N))
    for n in range(1, 2 * terme, 2):
        a = n * math.pi
        # sinh(a(1-y))/sinh(a) numerisch stabil
        f = np.exp(-a * y) * (1 - np.exp(-2 * a * (1 - y))) / (1 - math.exp(-2 * a))
        s += 400.0 / a * np.sin(a * x) * f
    return s


erg = {}
for N in (17, 33, 65, 129):
    u, steps = ftcs(N)
    ua = analytisch(N)
    h = 1.0 / (N - 1)
    e = np.abs(u - ua)[1:-1, 1:-1]
    yy = (np.arange(N)[:, None] * h * np.ones((1, N)))[1:-1, 1:-1]
    xx = (np.ones((N, 1)) * np.arange(N)[None, :] * h)[1:-1, 1:-1]
    d = np.minimum(np.hypot(xx, yy), np.hypot(1 - xx, yy))  # Abstand zur naechsten heissen Ecke (0,0) bzw. (1,0)
    kern = (xx >= .25) & (xx <= .75) & (yy >= .25) & (yy <= .75)
    rms = lambda m: float(np.sqrt(np.mean(e[m] ** 2)))
    alle = np.ones_like(e, dtype=bool)
    erg[N] = dict(steps=steps, rms_alle=rms(alle), rms_o01=rms(d >= .1), rms_o025=rms(d >= .25),
                  max_kern=float(e[kern].max()), max_ecke=float(e[d < .1].max()), n_ecke=int((d < .1).sum()),
                  e11=float(e[0, 0]), d11=float(d[0, 0]))
    print(N, {k: (f"{v:.4e}" if isinstance(v, float) else v) for k, v in erg[N].items()})
Ns = [17, 33, 65, 129]
for k in ("rms_alle", "rms_o01", "rms_o025", "max_kern"):
    print(k, "Verhaeltnisse:", [round(erg[a][k] / erg[b][k], 2) for a, b in zip(Ns, Ns[1:])])
np.save(sys.argv[1] if len(sys.argv) > 1 else "e8_erg.npy", erg, allow_pickle=True)
