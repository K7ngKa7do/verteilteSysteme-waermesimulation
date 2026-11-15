import klib, io, contextlib
g={}
for f in ("k2.py","k4.py"):
    with contextlib.redirect_stdout(io.StringIO()): exec(open(f).read(),g)
print("Komm%-Werte, die NICHT mit Median(komm)/Median(zeit) übereinstimmen:",len(klib.ONLY_OTHER))
for x in klib.ONLY_OTHER: print("  ",x)
