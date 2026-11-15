from klib import *
import time
r=load("e13b_cpu_N2048_P1_2026-11-01.csv"); v=np.array([float(x['zeit_s']) for x in r]); print("E13b Median aller 200 Läufe:",round(med(v),4))
t0=time.time()
def analytic(N,terms=1001):
    x=np.linspace(0,1,N); y=np.linspace(0,1,N)  # u[i,j]: i ~ y (Zeile), j ~ x (Spalte); Zeile 0 = 100
    X,Y=np.meshgrid(x,y)
    U=np.zeros_like(X)
    for n in range(1,2*terms,2):
        a=n*np.pi
        U+= 400/a*np.sin(a*X)*(np.exp(-a*Y)-np.exp(-a*(2-Y)))/(1-np.exp(-2*a))
    return U
def ftcs(N,steps,r=0.2):
    u=np.zeros((N,N)); u[0,:]=100.0
    for _ in range(steps):
        v=u.copy()
        v[1:-1,1:-1]=u[1:-1,1:-1]+r*(u[:-2,1:-1]+u[2:,1:-1]+u[1:-1,:-2]+u[1:-1,2:]-4*u[1:-1,1:-1])
        u=v
    return u
exp_core={17:"1,204e-1",33:"3,074e-2",65:"7,740e-3",129:"1,955e-3"}
exp_rms={17:"1,413e-1",33:"6,838e-2",65:"3,365e-2",129:"1,669e-2"}
exp_steps={17:907,33:3631,65:14525,129:58101}
h_prev=None; cores=[]; rmss=[]
for N in (17,33,65,129):
    h=1/(N-1); steps=int(14/(0.2*2*np.pi**2*h*h)); 
    if steps!=exp_steps[N]: print("   Schritte weichen ab",N,steps,exp_steps[N])
    chk(f"E8 Schritte N={N}",str(exp_steps[N]),steps)
    u=ftcs(N,steps); a=analytic(N)
    err=np.abs(u-a)
    xs=np.linspace(0,1,N); core=(xs>=0.25-1e-12)&(xs<=0.75+1e-12)
    ce=err[np.ix_(core,core)].max(); inner=err[1:-1,1:-1]; rm=np.sqrt(np.mean(inner**2))
    cores.append(ce); rmss.append(rm)
    chk(f"E8 N={N} Max-Fehler Kern",exp_core[N],ce,1.0) if False else None
    print(f"   N={N}: steps={steps} core_max={ce:.3e} (Prot {exp_core[N]}) rms={rm:.3e} (Prot {exp_rms[N]})")
    p=num(exp_core[N].replace('e-','e-'));
for i,N in enumerate((17,33,65,129)):
    m=cores[i]/10**int(exp_core[N].split('e')[1]); chk(f"E8 N={N} core",exp_core[N].split('e')[0],m)
    m=rmss[i]/10**int(exp_rms[N].split('e')[1]); chk(f"E8 N={N} rms",exp_rms[N].split('e')[0],m)
for i,pr in enumerate(["3,92","3,97","3,96"]): chk(f"E8 Verhältnis core {i}",pr,cores[i]/cores[i+1])
for i,pr in enumerate(["2,07","2,03","2,02"]): chk(f"E8 Verhältnis rms {i}",pr,rmss[i]/rmss[i+1])
report("E8 Teil 1")
# Stabilität
N=33
exp={0.20:["1,000e+02"]*4,0.24:["1,000e+02"]*4,0.25:["1,000e+02"]*4,0.26:["1,000e+02","1,000e+02","5,740e+02","6,724e+05"],0.30:["3,158e+04","1,618e+11","2,140e+25","5,230e+39"]}
for r_,ex in exp.items():
    u=np.zeros((N,N)); u[0,:]=100.0; out=[]
    for s in range(1,301):
        v=u.copy(); v[1:-1,1:-1]=u[1:-1,1:-1]+r_*(u[:-2,1:-1]+u[2:,1:-1]+u[1:-1,:-2]+u[1:-1,2:]-4*u[1:-1,1:-1]); u=v
        if s in (50,100,200,300): out.append(np.abs(u).max())
    print(f"   r={r_}: "+"  ".join(f"{o:.3e}" for o in out)+"   (Prot: "+"  ".join(ex)+")")
print("Dauer",round(time.time()-t0),"s")
print("Verstärkungsfaktor |1-8r|:",abs(1-8*0.26),abs(1-8*0.30))
