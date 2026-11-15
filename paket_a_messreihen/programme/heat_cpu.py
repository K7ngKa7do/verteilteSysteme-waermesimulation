import sys
import numpy as np
from numba import njit
from mpi4py import MPI

@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

def cpu():
    s = open('/proc/self/stat').read()
    return int(s.rsplit(') ', 1)[1].split()[36])

def sysfs(c, pfad):
    try:
        return open(f'/sys/devices/system/cpu/cpu{c}/{pfad}').read().strip().replace(',', '+')
    except Exception:
        return 'na'

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
c0 = cpu()
mhz0 = sysfs(c0, 'cpufreq/scaling_cur_freq')
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
c1 = cpu()
mhz1 = sysfs(c1, 'cpufreq/scaling_cur_freq')

s = comm.reduce(float(u[1:nloc + 1].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    pkg = sysfs(c0, 'topology/physical_package_id')
    sib = sysfs(c0, 'topology/thread_siblings_list')
    print(f"{size},{N},{steps},{t_total:.6f},{tc_max:.6f},{s:.10e},{c0},{c1},{mhz0},{mhz1},{pkg},{sib}", flush=True)
