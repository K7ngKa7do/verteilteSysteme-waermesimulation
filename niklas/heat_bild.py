
import sys
from pathlib import Path
import numpy as np
from numba import njit
from mpi4py import MPI

@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
N = int(sys.argv[1])
steps = int(sys.argv[2])
r = 0.2

inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)

u = np.zeros((nloc + 2, N))
if rank == 0:
    u[0, :] = 100.0
v = u.copy()

up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL

kernel(np.zeros((4, 4)), np.zeros((4, 4)), r)

comm.Barrier()
t_comm = 0.0
t0 = MPI.Wtime()
for _ in range(steps):
    tc = MPI.Wtime()
    comm.Sendrecv(u[1], dest=up, recvbuf=u[nloc + 1], source=down)
    comm.Sendrecv(u[nloc], dest=down, recvbuf=u[0], source=up)
    t_comm += MPI.Wtime() - tc
    kernel(u, v, r)
    u, v = v, u
comm.Barrier()
t_total = MPI.Wtime() - t0

s = comm.reduce(float(u[1:nloc + 1].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    cells = inner * (N - 2) * steps
    print(f"P={size} N={N} Schritte={steps} Zeit={t_total:.3f} s Kommunikation(max)={tc_max:.3f} s Mio.Updates/s={cells / t_total / 1e6:.0f} Summe={s:.10e}", flush=True)

# Nur die berechneten Zeilen sammeln, ohne die beiden Geisterzeilen.
teile = comm.gather(u[1:nloc + 1].copy(), root=0)
if rank == 0:
    gitter = np.zeros((N, N))
    gitter[0, :] = 100.0
    gitter[1:-1, :] = np.vstack(teile)
    dateiname = f"gitter_N{N}_P{size}_S{steps}.npy"
    np.save(Path(__file__).resolve().parent / dateiname, gitter)
