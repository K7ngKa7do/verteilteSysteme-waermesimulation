import sys, time
import numpy as np
from numba import njit

@njit
def kernel(u, v, r):
    n = u.shape[1]
    for i in range(1, u.shape[0] - 1):
        for j in range(1, n - 1):
            v[i, j] = u[i, j] + r * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4.0 * u[i, j])

def numpy_schritt(u, v, r):
    v[1:-1, 1:-1] = u[1:-1, 1:-1] + r * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] - 4.0 * u[1:-1, 1:-1])

modus = sys.argv[1]; N = int(sys.argv[2]); steps = int(sys.argv[3]); r = 0.2
u = np.zeros((N, N)); u[0, :] = 100.0; v = u.copy()
schritt = kernel if modus == 'numba' else numpy_schritt
schritt(np.zeros((4, 4)), np.zeros((4, 4)), r)
t0 = time.perf_counter()
for _ in range(steps):
    schritt(u, v, r)
    u, v = v, u
t = time.perf_counter() - t0
print(f"{modus},{N},{steps},{t:.6f},{u[1:N-1].sum():.10e}", flush=True)
