import sys
import numpy as np
import numba
from numba import njit, prange
from mpi4py import MPI


@njit(parallel=True)
def kernel(u, v, r):
    n = u.shape[1]
    for i in prange(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i + 1, j] + u[i - 1, j] + u[i, j + 1] + u[i, j - 1] - 4.0 * u[i, j])


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
N = int(sys.argv[1])
steps = int(sys.argv[2])
T = int(sys.argv[3])
numba.set_num_threads(T)
r = 0.2

inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)
rows = nloc + 2
u = np.zeros((rows, N))
if rank == 0:
    u[0, :] = 100.0
v = u.copy()
up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL

kernel(np.zeros((6, 6)), np.zeros((6, 6)), r)
comm.Barrier()
tc = 0.0
t0 = MPI.Wtime()
for _ in range(steps):
    a = MPI.Wtime()
    comm.Sendrecv(u[1, :], dest=up, recvbuf=u[rows - 1, :], source=down)
    comm.Sendrecv(u[nloc, :], dest=down, recvbuf=u[0, :], source=up)
    tc += MPI.Wtime() - a
    kernel(u, v, r)
    u, v = v, u
    if rank == 0:
        u[0, :] = 100.0
    if rank == size - 1:
        u[rows - 1, :] = 0.0
comm.Barrier()
t_total = MPI.Wtime() - t0
tc_max = comm.reduce(tc, op=MPI.MAX, root=0)
s = comm.reduce(float(u[1:1 + nloc, :].sum()), op=MPI.SUM, root=0)
if rank == 0:
    print(f"{size},{N},{steps},{t_total:.6f},{tc_max:.6f},{s:.10e},{T}", flush=True)
