import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
P = comm.Get_size()
n = 2048 * 2048
a = np.ones(n); b = np.zeros(n)
np.copyto(b, a)
for versuch in range(20):
    comm.Barrier()
    t = MPI.Wtime()
    for _ in range(20):
        np.copyto(b, a)
    dt = MPI.Wtime() - t
    dtmax = comm.reduce(dt, op=MPI.MAX, root=0)
    if comm.Get_rank() == 0:
        gesamt = P * 20 * 2 * n * 8 / dtmax / 1e9
        print(f"{P},{versuch},{gesamt:.3f},{gesamt / P:.3f}", flush=True)
