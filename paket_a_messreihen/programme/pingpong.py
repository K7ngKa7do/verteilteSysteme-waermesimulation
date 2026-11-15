import sys
import numpy as np
from mpi4py import MPI

# Aufruf: mpirun -np 2 ... python pingpong.py MODUS
# Ausgabe (nur Rank 0): modus,groesse_byte,versuch,zeit_einfach_s
modus = sys.argv[1]
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
groessen = [8, 64, 512, 4096, 32768, 262144, 1048576, 4194304, 16777216]
versuche = 20

def wiederholungen(n):
    if n <= 1024:
        return 2000
    if n <= 65536:
        return 500
    if n <= 1048576:
        return 50
    return 10

for n in groessen:
    buf = np.zeros(n, dtype=np.uint8)
    k = wiederholungen(n)
    for _ in range(5):                      # Aufwärmen, nicht gemessen
        if rank == 0:
            comm.Send(buf, dest=1); comm.Recv(buf, source=1)
        else:
            comm.Recv(buf, source=0); comm.Send(buf, dest=0)
    for v in range(versuche):
        comm.Barrier()
        t0 = MPI.Wtime()
        for _ in range(k):
            if rank == 0:
                comm.Send(buf, dest=1); comm.Recv(buf, source=1)
            else:
                comm.Recv(buf, source=0); comm.Send(buf, dest=0)
        t = (MPI.Wtime() - t0) / (2 * k)    # eine Richtung
        if rank == 0:
            print(f"{modus},{n},{v},{t:.9e}", flush=True)
