import sys
import numpy as np
from numba import njit
from mpi4py import MPI

@njit
def kernel(u, v, r, i0, i1):
    n = u.shape[1]
    for i in range(i0, i1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

comm = MPI.COMM_WORLD; rank = comm.Get_rank(); size = comm.Get_size()
N = int(sys.argv[1]); steps = int(sys.argv[2]); r = 0.2
inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)
u = np.zeros((nloc + 2, N))
if rank == 0: u[0, :] = 100.0
v = u.copy()
up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL
kernel(np.zeros((4, 4)), np.zeros((4, 4)), r, 1, 3)   # warm-up
comm.Barrier(); t_comm = 0.0; t0 = MPI.Wtime()
for _ in range(steps):
    tc = MPI.Wtime()
    reqs = [comm.Irecv(u[0], source=up), comm.Irecv(u[nloc + 1], source=down),
            comm.Isend(u[1], dest=up), comm.Isend(u[nloc], dest=down)]
    t_comm += MPI.Wtime() - tc
    kernel(u, v, r, 2, nloc)
    tc = MPI.Wtime()
    MPI.Request.Waitall(reqs)
    t_comm += MPI.Wtime() - tc
    kernel(u, v, r, 1, 2)
    if nloc > 1:
        kernel(u, v, r, nloc, nloc + 1)
    u, v = v, u
comm.Barrier(); t_total = MPI.Wtime() - t0
s = comm.reduce(float(u[1:nloc + 1].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    cells = inner * (N - 2) * steps
    print(f"{size},{N},{steps},{t_total:.6f},{tc_max:.6f},{s:.10e}", flush=True)
