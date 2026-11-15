"""E8, Klaerungsphase 14.11.2026 (Gruppe A): Fehler der FTCS-Rechnung gegen die Reihenloesung,
mit und ohne Eckbereich (d < 0,1 bzw. d < 0,25 = Abstand zur naechsten heissen Ecke).
Ergebnis: Ordnung 2 abseits der beiden Sprungecken, an den Ecken bleibt ein Fehler von etwa 0,72.

Aufruf (nur NumPy): python3 e8_ecken.py   (Ausgabe gespeichert in e8_ecken_ausgabe.txt).
Arbeitsbericht Kapitel 6.15."""
import numpy as np, math
r=0.2
def ana(X,Y,terms=1001):
    u=np.zeros_like(X)
    for n in range(1,2*terms,2):
        # sinh(nπ(1-y))/sinh(nπ) = exp(-nπy)*(1-exp(-2nπ(1-y)))/(1-exp(-2nπ))
        f=np.exp(-n*np.pi*Y)*(1-np.exp(-2*n*np.pi*(1-Y)))/(1-np.exp(-2*n*np.pi))
        u+=400/(n*np.pi)*np.sin(n*np.pi*X)*f
    return u
res=[]
for N,steps in [(17,907),(33,3631),(65,14525),(129,58101)]:
    h=1/(N-1); u=np.zeros((N,N)); u[0,:]=100.0
    for _ in range(steps):
        u[1:-1,1:-1]=u[1:-1,1:-1]+r*(u[2:,1:-1]+u[:-2,1:-1]+u[1:-1,2:]+u[1:-1,:-2]-4*u[1:-1,1:-1])
    y=np.arange(N)*h; x=np.arange(N)*h; Y,X=np.meshgrid(y,x,indexing='ij')
    e=np.abs(u-ana(X,Y))[1:-1,1:-1]; Xi=X[1:-1,1:-1]; Yi=Y[1:-1,1:-1]
    dist=np.minimum(np.hypot(Xi,Yi),np.hypot(1-Xi,Yi))  # Abstand zur naechsten heissen Ecke
    row=[N]
    row.append(np.sqrt(np.mean(e**2)))
    for d in (0.1,0.25):
        m=dist>=d; row.append(np.sqrt(np.mean(e[m]**2)))
    core=(Xi>=0.25)&(Xi<=0.75)&(Yi>=0.25)&(Yi<=0.75); row.append(e[core].max())
    # Fehler nahe Ecke: Max im Ring
    row.append(e[dist<0.1].max())
    res.append(row)
print("N | RMS alle | RMS ohne Ecken d<0.1 | RMS ohne d<0.25 | Max Kern | Max nahe Ecke (d<0.1)")
for i,rw in enumerate(res):
    s=" | ".join(f"{v:.3e}" for v in rw[1:])
    q="" if i==0 else "  Verh.: "+" ".join(f"{res[i-1][k]/rw[k]:.2f}" for k in range(1,6))
    print(rw[0],"|",s,q)
