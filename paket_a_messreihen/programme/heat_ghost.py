import sys
import numpy as np
from numba import njit
from mpi4py import MPI

@njit
def kernel(u, v, r, lo, hi):
    n = u.shape[1]
    for i in range(lo, hi):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
N = int(sys.argv[1])
steps = int(sys.argv[2])
g = int(sys.argv[3])
r = 0.2

inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)

bad = comm.allreduce(1 if nloc < g else 0, op=MPI.MAX)
if bad or steps % g != 0:
    if rank == 0:
        print("Fehler: zu wenig Zeilen je Prozess oder Schritte nicht durch g teilbar", flush=True)
    sys.exit(1)

rows = nloc + 2 * g
u = np.zeros((rows, N))
if rank == 0:
    u[g - 1, :] = 100.0
v = u.copy()

up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL

kernel(np.zeros((6, 6)), np.zeros((6, 6)), r, 1, 5)

comm.Barrier()
t_comm = 0.0
t0 = MPI.Wtime()
for _ in range(steps // g):
    tc = MPI.Wtime()
    comm.Sendrecv(u[g:2 * g], dest=up, recvbuf=u[rows - g:rows], source=down)
    comm.Sendrecv(u[nloc:nloc + g], dest=down, recvbuf=u[0:g], source=up)
    t_comm += MPI.Wtime() - tc
    for s in range(g):
        kernel(u, v, r, s + 1, rows - 1 - s)
        u, v = v, u
        if rank == 0:
            u[g - 1, :] = 100.0
        if rank == size - 1:
            u[g + nloc, :] = 0.0
comm.Barrier()
t_total = MPI.Wtime() - t0

s = comm.reduce(float(u[g:g + nloc].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    print(f"{size},{N},{steps},{t_total:.6f},{tc_max:.6f},{s:.10e},{g}", flush=True)
