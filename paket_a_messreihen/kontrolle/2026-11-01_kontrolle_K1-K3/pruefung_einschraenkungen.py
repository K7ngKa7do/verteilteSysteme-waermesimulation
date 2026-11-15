# Prüfung der Einschränkungen aus K2 (01.11.2026)
# (1) Ist die Zweiteilung mehr als Zufall? Conservative Simulation: Nullmodell = eine Lognormalverteilung,
#     Streuung aus der GESAMTEN Stichprobe geschätzt (bimodale Daten -> große Streuung -> Test eher konservativ).
#     Statistik: größte Relativlücke (Quotient aufeinanderfolgender sortierter Werte) mit je >=3 Werten je Seite.
# (2) Wo steckt die Zusatzzeit: im Rechnen (zeit - komm_max) oder in der Kommunikation (komm_max)?
# (3) Wald-Wolfowitz-Runs-Test auf zeitliche Unabhängigkeit der Zustände.
import csv, os, math
import numpy as np
from math import erf, sqrt
base = os.path.expanduser("~/mnt/waerme_sicherung_2026-11-01/results")
fall = [("e1_groesse",1,2048),("e2_node",12,4096),("e2_slot",4,4096),("e2b_node",2,2048),
        ("e2c_node",12,8192),("e2c_node",24,8192),("e2c_ppr_P12",12,8192),
        ("e4_bloecke_P12",12,8192),("e5_overlap_P12",12,8192),("e5b_nb_P12",12,8192)]
rng = np.random.default_rng(12345)
def maxgap(x):
    s = np.sort(x); n = len(s)
    return max(s[k]/s[k-1] for k in range(3, n-2))
def runs_p(z):
    n1=int(z.sum()); n2=len(z)-n1
    if n1==0 or n2==0: return float("nan")
    r=1+int(np.sum(z[1:]!=z[:-1])); n=n1+n2
    mu=2*n1*n2/n+1; var=(mu-1)*(mu-2)/(n-1)
    zz=(r-mu)/sqrt(var) if var>0 else 0
    return 0.5*(1+erf(zz/sqrt(2))), r, mu   # einseitig: wenige Runs = Klumpung
for name,P,N in fall:
    rows=[r for r in csv.DictReader(open(f"{base}/{name}_2026-11-01.csv")) if int(r["P"])==P and int(r["N"])==N]
    t=np.array([float(r["zeit_s"]) for r in rows]); k_=np.array([float(r["komm_max_s"]) for r in rows])
    s=np.sort(t); k=np.argmax(s[1:]/s[:-1])+1; thr=(s[k]+s[k-1])/2; lang=t>thr
    g_obs=maxgap(t)
    lt=np.log(t); mu,sd=lt.mean(),lt.std(ddof=1)
    sim=np.array([maxgap(np.exp(rng.normal(mu,sd,len(t)))) for _ in range(20000)])
    p_gap=(np.sum(sim>=g_obs)+1)/(len(sim)+1)
    # Trennschärfe: Lücke gegen größte Streuung innerhalb der Zustände
    def spread(a): return a.max()/a.min() if len(a)>1 else 1.0
    sep=g_obs/max(spread(t[~lang]),spread(t[lang]))
    # (2) Zusatzzeit
    comp=t-k_
    d_total=np.median(t[lang])-np.median(t[~lang])
    d_komm=np.median(k_[lang])-np.median(k_[~lang])
    d_comp=np.median(comp[lang])-np.median(comp[~lang])
    anteil_komm=100*d_komm/d_total if d_total>0 else float("nan")
    rp=runs_p(lang)
    rp_txt=f"p={rp[0]:.3f} (Runs {rp[1]} / erwartet {rp[2]:.1f})" if isinstance(rp,tuple) else "n/a"
    print(f"{name} P={P} N={N}: Lücke={g_obs:.3f}  p_Lücke={p_gap:.4f}  Trennschärfe={sep:.2f}  |  Zusatzzeit gesamt {d_total:.3f}s = Komm {d_komm:+.3f}s ({anteil_komm:.0f} %) + Rechnen {d_comp:+.3f}s  |  Runs-Test {rp_txt}")
