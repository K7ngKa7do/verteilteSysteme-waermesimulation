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

def teile(inner, d, idx):
    base, rem = divmod(inner, d)
    return base + (1 if idx < rem else 0)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
N = int(sys.argv[1])
steps = int(sys.argv[2])
r = 0.2

if len(sys.argv) > 3:
    px = int(sys.argv[3])
    dims = [px, size // px]
else:
    dims = MPI.Compute_dims(size, 2)
cart = comm.Create_cart(dims, periods=[False, False], reorder=False)
cy, cx = cart.Get_coords(rank)
up, down = cart.Shift(0, 1)
left, right = cart.Shift(1, 1)

inner = N - 2
nr = teile(inner, dims[0], cy)
nc = teile(inner, dims[1], cx)

u = np.zeros((nr + 2, nc + 2))
if cy == 0:
    u[0, :] = 100.0
v = u.copy()

sb = np.empty(nr)
rb = np.empty(nr)

kernel(np.zeros((4, 4)), np.zeros((4, 4)), r)

comm.Barrier()
t_comm = 0.0
t0 = MPI.Wtime()
for _ in range(steps):
    tc = MPI.Wtime()
    cart.Sendrecv(u[1, 1:nc + 1], dest=up, recvbuf=u[nr + 1, 1:nc + 1], source=down)
    cart.Sendrecv(u[nr, 1:nc + 1], dest=down, recvbuf=u[0, 1:nc + 1], source=up)
    sb[:] = u[1:nr + 1, nc]
    cart.Sendrecv(sb, dest=right, recvbuf=rb, source=left)
    if left != MPI.PROC_NULL:
        u[1:nr + 1, 0] = rb
    sb[:] = u[1:nr + 1, 1]
    cart.Sendrecv(sb, dest=left, recvbuf=rb, source=right)
    if right != MPI.PROC_NULL:
        u[1:nr + 1, nc + 1] = rb
    t_comm += MPI.Wtime() - tc
    kernel(u, v, r)
    u, v = v, u
comm.Barrier()
t_total = MPI.Wtime() - t0

s = comm.reduce(float(u[1:nr + 1, 1:nc + 1].sum()), op=MPI.SUM, root=0)
tc_max = comm.reduce(t_comm, op=MPI.MAX, root=0)
if rank == 0:
    print(f"{size},{N},{steps},{t_total:.6f},{tc_max:.6f},{s:.10e}", flush=True)
