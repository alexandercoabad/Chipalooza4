import numpy as np, simlib, itertools
import os
RCX=os.environ.get("RCX",os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","mag","mixedsignal_rcx.spice"))
def body(s0,s1,cext='100n'):
    return f""".include {RCX}
Vdd vdd 0 1.8
Vs0 s0 0 {1.8*s0}
Vs1 s1 0 {1.8*s1}
Vin vin 0 dc 0 ac 1
Cext vin ain {cext}
Xdut vdd 0 s0 s1 ain aout mixedsignal
.control
op
print v(aout)
ac dec 20 10 1e8
let gdb=db(v(aout)/v(vin))
wrdata OUT gdb
.endc
"""
for s1,s0 in itertools.product((0,1),(0,1)):   # code = (ui_in[1],ui_in[0])
    a,so=simlib.run(body(s0,s1),'tt',27)
    f,g=a[:,0],a[:,1]; i=np.argmin(abs(f-1e5))
    vb=[l for l in so.splitlines() if 'v(aout)' in l][-1].split('=')[-1].strip()
    print(f"ui_in[1:0]={s1}{s0}: gain@100k={g[i]:.1f} dB  peak {g.max():.1f} dB@{f[np.argmax(g)]:.0f}Hz  bias={vb}")
