import sys
import numpy as np
from numba import njit
from mpi4py import MPI

# B7b-Gegentest: wie heat_adresse.py, aber u und v liegen in EINEM Puffer,
# v absichtlich OFF Byte gegen u versetzt (bezogen auf 2 MiB).
# Aufruf: heat_versatz.py N SCHRITTE OFF   (OFF Vielfaches von 8, z. B. 0, 4096, 32768)
@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

def anon_huge_kb():
    try:
        for zeile in open('/proc/self/smaps_rollup'):
            if zeile.startswith('AnonHugePages'):
                return int(zeile.split()[1])
    except OSError:
        pass
    return -1

comm = MPI.COMM_WORLD; rank = comm.Get_rank(); size = comm.Get_size()
N = int(sys.argv[1]); steps = int(sys.argv[2]); OFF = int(sys.argv[3]); r = 0.2
inner = N - 2
base, rem = divmod(inner, size)
nloc = base + (1 if rank < rem else 0)
M = 2 * 1024 * 1024
nbytes = (nloc + 2) * N * 8
R = -(-nbytes // M) * M                      # auf volle 2 MiB aufgerundet
buf = np.empty(2 * R + OFF + 2 * M, dtype=np.uint8)
a0 = (-buf.ctypes.data) % M                  # Beginn von u auf 2-MiB-Grenze
u = buf[a0:a0 + nbytes].view(np.float64).reshape(nloc + 2, N)
b0 = a0 + R + OFF                            # v: OFF Byte gegen u versetzt
v = buf[b0:b0 + nbytes].view(np.float64).reshape(nloc + 2, N)
u[:] = 0.0
if rank == 0:
    u[0, :] = 100.0
v[:] = u
au = u.ctypes.data; av = v.ctypes.data
up = rank - 1 if rank > 0 else MPI.PROC_NULL
down = rank + 1 if rank < size - 1 else MPI.PROC_NULL
kernel(np.zeros((4, 4)), np.zeros((4, 4)), r)
comm.Barrier(); t_comm = 0.0; t0 = MPI.Wtime()
for _ in range(steps):
    tc = MPI.Wtime()
    comm.Sendrecv(u[1], dest=up, recvbuf=u[nloc + 1], source=down)
    comm.Sendrecv(u[nloc], dest=down, recvbuf=u[0], source=up)
    t_comm += MPI.Wtime() - tc
    kernel(u, v, r)
    u, v = v, u
comm.Barrier(); t_total = MPI.Wtime() - t0
s = comm.reduce(float(u[1:nloc + 1].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    print(f"{size},{N},{steps},{OFF},{t_total:.6f},{tc_max:.6f},{s:.10e},"
          f"{au % M},{av % M},{(av - au) % M},{anon_huge_kb()}", flush=True)
