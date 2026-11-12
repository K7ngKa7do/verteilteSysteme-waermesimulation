"""Separate MPI-Demo zur Live-Anzeige, ohne Leistungsmessung."""

import argparse
import math
from pathlib import Path
import time

import numpy as np
from numba import njit
from mpi4py import MPI


N = 128
R = 0.2
PROZESSE = 4


# FTCS-Kern aus heat_bild.py.
@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])


def speichere_atomisch(pfad, daten):
    temporaer = pfad.with_suffix(".tmp")
    with temporaer.open("wb") as datei:
        np.save(datei, daten, allow_pickle=False)
    temporaer.replace(pfad)


def veroeffentliche_gitter(comm, rank, u, nloc, schritt, ausgabe):
    # Die beiden Geisterzeilen gehören nicht zum berechneten Streifen.
    teile = comm.gather(u[1:nloc + 1].copy(), root=0)
    if rank != 0:
        return

    gitter = np.zeros((N, N))
    gitter[0, :] = 100.0
    gitter[1:-1, :] = np.vstack(teile)

    if schritt == 0:
        # gather liefert die Streifen in Rangfolge. Feste Ränder erhalten -1.
        raenge = np.full((N, N), -1, dtype=np.int8)
        zeile = 1
        for rang, teil in enumerate(teile):
            naechste_zeile = zeile + teil.shape[0]
            raenge[zeile:naechste_zeile, 1:-1] = rang
            zeile = naechste_zeile
        speichere_atomisch(ausgabe / "raenge.npy", raenge)

    speichere_atomisch(ausgabe / f"gitter_S{schritt:05d}.npy", gitter)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ausgabe", type=Path, help="Vorhandener temporärer Ausgabeordner für diesen Lauf")
    parser.add_argument("--schritte", type=int, default=8000)
    parser.add_argument("--intervall", type=int, default=50)
    parser.add_argument("--demo-pause", type=float, default=0.0, help="Reine Demo-Pause in Sekunden pro Bild")
    args = parser.parse_args()
    if args.schritte < 0 or args.intervall < 1:
        parser.error("--schritte muss >= 0 und --intervall muss >= 1 sein")
    if not math.isfinite(args.demo_pause) or args.demo_pause < 0:
        parser.error("--demo-pause muss eine endliche Zahl >= 0 sein")
    if not args.ausgabe.is_dir():
        parser.error("Der temporäre Ausgabeordner muss bereits existieren")

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    if size != PROZESSE:
        parser.error(f"Diese Demo erwartet {PROZESSE} MPI-Prozesse, gestartet wurden {size}")

    # Dieselbe horizontale Zerlegung und dieselben Randwerte wie in heat_bild.py.
    inner = N - 2
    base, rem = divmod(inner, size)
    nloc = base + (1 if rank < rem else 0)
    u = np.zeros((nloc + 2, N))
    if rank == 0:
        u[0, :] = 100.0
    v = u.copy()

    up = rank - 1 if rank > 0 else MPI.PROC_NULL
    down = rank + 1 if rank < size - 1 else MPI.PROC_NULL

    veroeffentliche_gitter(comm, rank, u, nloc, 0, args.ausgabe)
    if rank == 0 and args.schritte > 0 and args.demo_pause:
        time.sleep(args.demo_pause)

    for schritt in range(1, args.schritte + 1):
        comm.Sendrecv(u[1], dest=up, recvbuf=u[nloc + 1], source=down)
        comm.Sendrecv(u[nloc], dest=down, recvbuf=u[0], source=up)
        kernel(u, v, R)
        u, v = v, u

        # Schritt 500 bleibt auch bei einem anderen Bildintervall vergleichbar.
        if schritt % args.intervall == 0 or schritt in (500, args.schritte):
            veroeffentliche_gitter(comm, rank, u, nloc, schritt, args.ausgabe)
            if rank == 0 and schritt < args.schritte and args.demo_pause:
                time.sleep(args.demo_pause)


if __name__ == "__main__":
    main()
