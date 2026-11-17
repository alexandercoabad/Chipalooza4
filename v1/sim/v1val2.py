import numpy as np, simlib, itertools
def rres(L): return f"sky130_fd_pr__res_xhigh_po_5p73 w=5.73 l={L}"
def body(s0,s1,Wtot,nf=1,cext='100n'):
    # mux (xschem top level): I1 open, I2 3k, I3 30k, I4 100k -> OUT = gate node (g); other side of each R to out
    return f""".include mux_v1.sub
Vdd vdd 0 1.8
Vs0 s0 0 {1.8*s0}
Vs1 s1 0 {1.8*s1}
Vin vin 0 dc 0 ac 1
Cext vin a {cext}
Xrin a g 0 {rres(8.6)}
Xrf g out 0 {rres(860)}
Xr30 i3 out 0 {rres(86)}
Xr3 i2 out 0 {rres(8.6)}
Xr100 i4 out 0 {rres(287)}
Xmux i1 i2 i3 i4 s1 s0 g vdd 0 x4-to-1_analog_MUX
Xp out g vdd vdd sky130_fd_pr__pfet_01v8 w={Wtot} l=0.5 nf=1 mult=1
Xn out g 0 0 sky130_fd_pr__nfet_01v8 w={Wtot} l=0.5 nf=1 mult=1
.control
op
print v(out) -i(Vdd)
ac dec 20 10 1e8
let gdb=db(v(out)/v(vin))
wrdata OUT gdb
.endc
"""
if __name__=='__main__':
  for Wtot in (4,20):
    print("Wtot",Wtot)
    for s1,s0 in itertools.product((0,1),(0,1)):
        a,so=simlib.run(body(s0,s1,Wtot),'tt',27)
        f,g=a[:,0],a[:,1]; i=np.argmin(abs(f-1e5))
        L=[l.split('=')[-1].strip() for l in so.splitlines() if l.strip().startswith(('v(out)','-i(vdd)'))]
        print(f"  ui_in[1:0]={2*s0+s1:02b} (S1={s1} S2={s0}): gain@100k={g[i]:.1f} dB  peak {g.max():.1f}@{f[np.argmax(g)]:.0f}Hz  Vb,Idd={L}")
