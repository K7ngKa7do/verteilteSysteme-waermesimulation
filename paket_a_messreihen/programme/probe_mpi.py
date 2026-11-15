import sys, time
import numpy as np
if sys.argv[1] == 'mpi':
    from mpi4py import MPI
from numba import njit

@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

N = 2048; r = 0.2
u = np.zeros((N, N)); u[0, :] = 100.0; v = u.copy()
au, av = u.ctypes.data, v.ctypes.data
kernel(np.zeros((4, 4)), np.zeros((4, 4)), r)
t0 = time.perf_counter()
for _ in range(200):
    kernel(u, v, r)
    u, v = v, u
t = time.perf_counter() - t0
print(f"{sys.argv[1]},{t:.4f},u%4096={au % 4096},v%4096={av % 4096},(v-u)%4096={(av - au) % 4096}", flush=True)
