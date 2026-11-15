"""Hilfsfunktionen fuer die Nachrechnung (Arbeitsbericht Paket A, 14.11.2026).

Wird von pruefe_teil1.py und pruefe_teil2.py importiert: CSV lesen, gruppieren, Median,
95-%-Rank-Intervall des Medians (Hoefler & Belli 2015, nach Le Boudec), Regel 1 (Updates/s),
exakter Fisher-Test und der Vergleich "berechnet gegen Berichtswert" (Klasse Pruefer)."""
import csv
import math
import os
from collections import defaultdict

import numpy as np

D = None  # Datenordner, wird vom Hauptskript gesetzt


def lies(name):
    """CSV als Liste von Dicts (Werte als str)."""
    with open(os.path.join(D, name), newline="") as f:
        return list(csv.DictReader(f))


def gruppen(rows, *keys, wert="zeit_s"):
    g = defaultdict(list)
    for r in rows:
        k = tuple(r[x] for x in keys)
        g[k].append(float(r[wert]))
    return g


def med(x):
    return float(np.median(np.asarray(x, dtype=float)))


def ki(x):
    """95-%-Rank-Intervall des Medians nach Hoefler & Belli 2015 (Le Boudec)."""
    a = np.sort(np.asarray(x, dtype=float))
    n = len(a)
    lo = math.floor((n - 1.96 * math.sqrt(n)) / 2)
    hi = math.ceil(1 + (n + 1.96 * math.sqrt(n)) / 2)
    if lo < 1 or hi > n:
        return (float("nan"), float("nan"))
    return (float(a[lo - 1]), float(a[hi - 1]))


def ups(N, steps, t):
    """Regel 1: Updates/s = (N-2)^2 * Schritte / Zeit."""
    return (N - 2) ** 2 * steps / t


def fisher2(a, b, c, d):
    """Exakter Fisher-Test 2x2, zweiseitig (Summe der Wahrscheinlichkeiten <= beobachtet)."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def p(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)

    p0 = p(a)
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9))


class Pruefer:
    def __init__(self):
        self.ok = 0
        self.fehler = []

    def gleich(self, name, ist, soll, stellen):
        """OK, wenn ist auf 'stellen' Nachkommastellen gerundet = soll."""
        tol = 0.5 * 10 ** (-stellen) + 1e-12
        if abs(ist - soll) <= tol:
            self.ok += 1
        else:
            self.fehler.append(f"{name}: berechnet {ist:.{stellen + 2}f}, Protokoll {soll}")

    def bericht(self, titel):
        print(f"[{titel}] geprueft {self.ok + len(self.fehler)}, OK {self.ok}, Abweichungen {len(self.fehler)}")
        for f in self.fehler:
            print("   -", f)
        self.ok, self.fehler = 0, []
