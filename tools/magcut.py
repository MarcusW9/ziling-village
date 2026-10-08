import numpy as np, scipy.ndimage as nd, sys
from PIL import Image
src,out,names,rowh=sys.argv[1],sys.argv[2],sys.argv[3].split(','),int(sys.argv[4])
im=np.array(Image.open(src).convert('RGB')).astype(int);r,g,b=im[:,:,0],im[:,:,1],im[:,:,2]
fg=~((r-g>90)&(b-g>90))
for _ in range(2):
    e=fg&~nd.binary_erosion(fg);fg&=~(e&(r-g>40)&(b-g>40))
L,n=nd.label(nd.binary_dilation(fg,iterations=8))
objs=sorted([(o,i+1) for i,o in enumerate(nd.find_objects(L)) if (o[0].stop-o[0].start)*(o[1].stop-o[1].start)>1500],key=lambda t:((t[0][0].start+t[0][0].stop)//2//rowh,t[0][1].start))
print(len(objs))
for (o,i),nm in zip(objs,names):
    m=(L[o]==i)&fg[o];a=np.dstack([im[o],np.where(m,255,0)]).astype('int')
    t=(a[:,:,0]>a[:,:,1]+8)&(a[:,:,2]>a[:,:,1]+8)&m&(a[:,:,0]>150)&(a[:,:,2]>120)
    if 'lotus' not in nm:a[t,3]=0
    o2=Image.fromarray(a.astype('uint8'),'RGBA');o2.crop(o2.getbbox()).save(f'{out}/{nm}.png')
