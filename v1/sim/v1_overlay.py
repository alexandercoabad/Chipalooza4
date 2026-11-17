"""Post-layout (extracted RC netlist) v1 AC response per mux code, 100 nF coupling, AD3-style output load.
Usage: SKY130PR=... python3 v1_overlay.py   (RCX defaults to ../mag/mixedsignal_rcx.spice)"""
import numpy as np, simlib, os, pickle
RCX=os.environ.get("RCX",os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","mag","mixedsignal_rcx.spice"))
def body(code,cext='100n',load=True):
    s0=code&1; s1=(code>>1)&1
    ld="Rl aout 0 1Meg\nCl aout 0 24p\n" if load else ""
    return f""".include {RCX}
Vdd vdd 0 1.8
Vs0 s0 0 {1.8*s0}
Vs1 s1 0 {1.8*s1}
Vin vin 0 dc 0 ac 1
Cext vin ain {cext}
Xdut vdd 0 s0 s1 ain aout mixedsignal
{ld}.control
op
ac dec 20 2 3e7
let gdb=db(v(aout)/v(vin))
wrdata OUT gdb
.endc
"""
if __name__=='__main__':
    out={}
    for code in range(4):
        for load in (True,False):
            a,so=simlib.run(body(code,load=load),'tt',27)
            out[(code,load)]=(a[:,0],a[:,1])
        f,g=out[(code,True)]; i=np.argmin(abs(f-1e5)); j=np.argmin(abs(f-3.69e3))
        print(f"code {code}: gain @3.7k {g[j]:.1f} dB, @100k {g[i]:.1f} dB, peak {g.max():.1f} dB @ {f[np.argmax(g)]:.0f} Hz")
    pickle.dump(out,open('v1_overlay.pkl','wb'))
