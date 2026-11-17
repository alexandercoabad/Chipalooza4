import numpy as np, glob, pickle
from PIL import Image
from scipy.ndimage import median_filter
def grp(v):
    if len(v)==0: return []
    out=[];cur=[v[0]]
    for a in v[1:]:
        if a-cur[-1]<=2: cur.append(a)
        else: out.append(np.mean(cur)); cur=[a]
    out.append(np.mean(cur)); return out
def digitize(f, fc, c2c):
    im=np.array(Image.open(f).convert('RGB')).astype(int)
    # decade gridlines
    best=None
    for r in range(300,360,10):
        row=im[r]; g=[x for x in range(0,1280) if abs(row[x,0]-row[x,1])<6 and abs(row[x,1]-row[x,2])<6 and 150<row[x,0]<235]
        gg=grp(g); 
        for i in range(len(gg)):
            run=[gg[i]]
            for j in range(i+1,len(gg)):
                if 105<gg[j]-run[-1]<128: run.append(gg[j])
            if len(run)>=6 and (best is None or len(run)>len(best)): best=run
    if best is None: return None
    sp=np.median(np.diff(best))
    # red cursor line
    red=((im[:,:,0]>170)&(im[:,:,1]<80)&(im[:,:,2]<110)).sum(axis=0)
    xc=np.argmax(red); 
    if red[xc]<100: return None
    x10=xc-np.log10(fc/10)*sp
    blue=((im[:,:,0]<130)&(im[:,:,1]<120)&(im[:,:,2]>180))
    xl=int(x10-0.69*sp); xr=int(min(x10+6.4*sp,1275)); xl=max(xl,0)
    sub=blue[:,xl:xr]
    rows=sub.sum(axis=1)
    # bands
    bands=[];inb=False
    for y,v in enumerate(rows):
        if v>0 and not inb: s=y;inb=True
        if v==0 and inb: bands.append((s,y));inb=False
    bands=[b for b in bands if rows[b[0]:b[1]].sum()>400]
    if not bands: return None
    y0,y1=bands[0]
    ys=np.full(xr-xl,np.nan)
    for k in range(xr-xl):
        yy=np.where(sub[y0:y1,k])[0]
        if len(yy): ys[k]=y0+np.median(yy)
    xs=np.arange(xl,xr)
    ok=~np.isnan(ys)
    if ok.sum()<0.6*len(ys): return None
    ys=np.interp(xs,xs[ok],ys[ok])
    pxdb=1.875*sp/115.3
    yc=np.interp(xc,xs,ys)
    db=c2c-(ys-yc)/pxdb
    f=10*10**((xs-x10)/sp)
    return f,db,sp
if __name__=='__main__':
    clusters={0:(range(10,22),2375.1,31.457,2.1824),3:(range(23,35),3691.7,24.645,1.7727),1:(range(35,47),3691.7,20.886,1.788),2:(range(48,60),3691.7,18.061,1.7986)}
    out={}
    for code,(rng,fc,c2,c1) in clusters.items():
        curves=[]
        for i in rng:
            r=digitize(f's{i:02d}.png',fc,c2)
            if r is None: continue
            f,db,sp=r
            if not (108<sp<122): continue
            g=np.logspace(np.log10(5),np.log10(2e7),120)
            m=(g>=f.min())&(g<=f.max())
            c=np.full(len(g),np.nan); c[m]=np.interp(np.log10(g[m]),np.log10(f),db)-c1
            if np.nanmax(c)>(c2-c1)+4 or np.nanmin(c)<-60: continue
            curves.append(c); 
        A=np.array(curves); print(code,len(curves),'frames')
        out[code]=(g,np.nanmedian(A,axis=0),np.nanstd(A,axis=0))
    pickle.dump(out,open('digit.pkl','wb'))
    for code,(g,m,s) in out.items():
        i=np.nanargmax(m); print(code,'peak %.1f dB @ %.0f Hz; median spread %.2f dB'%(m[i],g[i],np.nanmedian(s)))
