from mpi4py import MPI
import numpy as np
import sys

comm = MPI.COMM_WORLD
m = int(sys.argv[1])
reps = int(sys.argv[2])
a = np.ones(m)
b = np.empty(m)
for _ in range(10):
    comm.Allreduce(a, b, op=MPI.SUM)
comm.Barrier()
t0 = MPI.Wtime()
for _ in range(reps):
    comm.Allreduce(a, b, op=MPI.SUM)
t = (MPI.Wtime() - t0) / reps
tmax = comm.reduce(t, op=MPI.MAX, root=0)
if comm.rank == 0:
    print(f"{comm.size},{m},{reps},{tmax:.9f},{b[0]:.1f}")
