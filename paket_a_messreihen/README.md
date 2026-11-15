# Paket A – Messreihen und Statistik

**Bearbeitung:** Kadan Sheikho (Paket A)
**Projekt:** Verteilte Simulation der Wärmeausbreitung (2D, explizites FTCS-Verfahren, r = 0,2) – Team ITM, Modul Verteilte Systeme, TH Köln, WiSe 2026/27
**Zeitraum:** 24.10.–14.11.2026

Dieser Ordner enthält die Programme, Rohdaten, Auswertungen, Abbildungen und Kontrollrechnungen der Leistungsmessungen auf dem Mac-Cluster der Gruppe (4 Rechner, je Intel Xeon E5-2697 v2 mit 12 Kernen, Gigabit-Ethernet; Python 3.12 mit NumPy, Numba und mpi4py, Open MPI 4.1.6).

## Inhalt

| Ordner | Inhalt |
|---|---|
| `programme/` | Messprogramme (Hauptprogramm `heat_csv.py`, Varianten `heat_*.py`), Ein-Prozess-Vergleich `baseline.py`, Netz- und Speichertests (`pingpong.py`, `bw_probe2.py`, `allreduce_test.py`), Messskripte `run_series*.sh` |
| `messdaten/` | Rohdaten aller Messreihen als CSV (je Zeile ein Lauf), Umgebungsdateien vom 24.10. und 28.10.2026 |
| `auswertung/` | Jupyter-Notebooks mit Tabellen und Grafiken (`auswertung.ipynb`: 28.10. und 01.11., `auswertung-2026-11-14.ipynb`: Messungen vom 09.11.) |
| `abbildungen/` | alle Grafiken (PNG) |
| `kontrolle/` | Kontrollrechnungen: alle Kennzahlen wurden aus den Rohdaten nachgerechnet (01.11.: K1–K3; 14.11.: 663 Werte, 0 Abweichungen) |

Dateinamen der Messdaten: `a_…` = Strong und Weak Scaling (28.10.), `e1_…` bis `e18_…` = Zusatzexperimente E1–E18 (01.–09.11.); das Datum im Namen ist der Messtag.

## Messverfahren (kurz)

- Zeitmessung mit `MPI.Wtime()` zwischen zwei `Barrier` um die Zeitschleife (200 Zeitschritte), ohne Programmstart und Numba-Übersetzung.
- 15–20 Wiederholungen je Konfiguration; angegeben wird der **Median** mit 95-%-Konfidenzintervall nach Hoefler & Belli (2015).
- Speedup gegen das beste Programm mit einem Prozess (Numba ohne MPI, „COST“ nach McSherry et al. 2015).
- Korrektheit: Prüfsumme des Gitters bei allen Prozesszahlen gleich; Vergleich mit der exakten Lösung (Fehlerordnung 2).

## Wichtigste Ergebnisse

1. **Speedup 11,3** mit 48 Prozessen auf 4 Rechnern (N = 4096); **Weak Scaling ≈ 100 %**.
2. **Engpass ist die Speicherbandbreite je Rechner** (≈ 48 GB/s, gesättigt ab 6–8 Prozessen), nicht das Netz. Der Wärmekern bewegt 25 Byte je Gitterpunkt und Schritt; daraus lässt sich die Laufzeit bei N = 4096 auf 3 % genau vorhersagen.
3. **Prozesse gleichmäßig auf alle Rechner verteilen** (`--map-by ppr:K:node`): bis Faktor 2,9 schneller als „Rechner nacheinander füllen“.
4. **Das Netz zählt nur bei kleinen Gittern**: Latenz 53 µs, 117 MB/s; bei N ≤ 512 sind 48 Prozesse langsamer als einer.
5. Überlappung von Rechnen und Senden, tiefe Ghost-Zonen und Blockzerlegung helfen nur bei kleinen bis mittleren Gittern; Hybrid (MPI + Threads) ist langsamer.
6. **Grenzen**: mehr Prozesse als logische Kerne kosten Faktor 9,5 durch aktives Warten; der Ausfall eines Prozesses bricht den ganzen Lauf ab.
7. Ein zeitweise auftretender **„langsamer Zustand“** (bis Faktor 1,66) wurde auf die gegenseitige Lage der beiden Gitterfelder im Speicher bei großen Speicherseiten zurückgeführt; Abhilfe: `NUMPY_MADVISE_HUGEPAGE=0`.

Die ausführliche Darstellung mit Methode, Begründungen und Quellen folgt im Kapitel „Messmethode und Ergebnisse“ der Projektdokumentation.

## Ausführen

Auf dem Cluster (Hostliste mit 4 × 12 Plätzen), Beispiel 48 Prozesse, N = 4096:

```bash
mpirun --hostfile ~/mpi-hosts-12 -np 48 --map-by ppr:12:node python heat_csv.py 4096 200
```

Ausgabe: eine CSV-Zeile `P,N,Schritte,Zeit_s,Komm_max_s,Summe`. Messreihen: `run_series_map.sh HOSTLISTE AUSGABE.csv "N-Werte" "P-Werte" WIEDERHOLUNGEN MAP`.
