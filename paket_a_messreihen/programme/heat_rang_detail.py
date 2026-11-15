import sys
import numpy as np
import numba
from numba import njit, prange
from mpi4py import MPI

# C2: wie heat_rang.py, gibt aber JEDEN Rang einzeln aus (Rechnen, Austausch, Rechner,
# Lage v gegen u bezogen auf 2 MiB, Abstand zum naechsten Vielfachen von 1 MiB, AnonHugePages).
# Ausgabezeilen: R,rang,rechner,t_comp,t_comm,(v-u)%2MiB,abstand_1MiB,anonhuge_kB
# wie heat_csv.py, aber Zeiten JE RANG: Rechnen, Austausch (Sendrecv) und optional Barrier.
# Aufruf: heat_rang.py N SCHRITTE T MODUS
#   T = 0: serieller Kern wie heat_csv.py; T > 0: paralleler Kern mit T Numba-Threads
#   MODUS = 0: normal; 1: vor jedem Austausch comm.Barrier() (trennt Warten von Uebertragung)
@njit
def kern_s(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

@njit(parallel=True)
def kern_p(u, v, r):
    n = u.shape[1]
    for i in prange(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

comm = MPI.COMM_WORLD; rank = comm.Get_rank(); size = comm.Get_size()
N = int(sys.argv[1]); steps = int(sys.argv[2]); T = int(sys.argv[3]); modus = int(sys.argv[4]); r = 0.2
if T > 0:
    numba.set_num_threads(T); kernel = kern_p
else:
    kernel = kern_s
inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)
u = np.zeros((nloc + 2, N))
if rank == 0:
    u[0, :] = 100.0
v = u.copy()
M = 2 * 1024 * 1024
dvu = (v.ctypes.data - u.ctypes.data) % M
d1 = dvu % (M // 2); abst = min(d1, M // 2 - d1)
up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL
kernel(np.zeros((6, 6)), np.zeros((6, 6)), r)
comm.Barrier()
t_comp = 0.0; t_comm = 0.0; t_bar = 0.0
t0 = MPI.Wtime()
for _ in range(steps):
    if modus == 1:
        a = MPI.Wtime(); comm.Barrier(); t_bar += MPI.Wtime() - a
    a = MPI.Wtime()
    comm.Sendrecv(u[1], dest=up, recvbuf=u[nloc + 1], source=down)
    comm.Sendrecv(u[nloc], dest=down, recvbuf=u[0], source=up)
    t_comm += MPI.Wtime() - a
    a = MPI.Wtime()
    kernel(u, v, r)
    t_comp += MPI.Wtime() - a
    u, v = v, u
comm.Barrier(); t_total = MPI.Wtime() - t0
s = comm.reduce(float(u[1:nloc + 1].sum()), op=MPI.SUM, root=0)
def anon_huge_kb():
    try:
        for zeile in open('/proc/self/smaps_rollup'):
            if zeile.startswith('AnonHugePages'):
                return int(zeile.split()[1])
    except OSError:
        pass
    return -1
alle = comm.gather((t_comp, t_comm, t_bar, MPI.Get_processor_name(), dvu, abst, anon_huge_kb()), root=0)
if rank == 0:
    c = np.array([x[0] for x in alle]); k = np.array([x[1] for x in alle]); b = np.array([x[2] for x in alle])
    lang = int(np.argmax(c))
    print(f"{size},{N},{steps},{T},{modus},{t_total:.6f},"
          f"{c.min():.6f},{np.median(c):.6f},{c.max():.6f},"
          f"{k.min():.6f},{np.median(k):.6f},{k.max():.6f},"
          f"{b.min():.6f},{np.median(b):.6f},{b.max():.6f},"
          f"{s:.10e},{lang},{alle[lang][3]}", flush=True)
    for i, x in enumerate(alle):
        print(f"R,{i},{x[3]},{x[0]:.4f},{x[1]:.4f},{x[4]},{x[5]},{x[6]}", flush=True)
