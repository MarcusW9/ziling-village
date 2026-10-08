import numpy as np, scipy.ndimage as nd, sys
from PIL import Image
for path in sys.argv[1:]:
    im=np.array(Image.open(path).convert('RGBA')).astype(int);c=im[:,:,:3];al=im[:,:,3]>0
    sat=c.max(2)-c.min(2);m=c.mean(2);light=(m>160)&(sat<30)
    # enclosed light pockets
    lab,n=nd.label(light&al);
    for _ in range(4):
        edge=al&~nd.binary_erosion(al);rm=edge&light
        if not rm.any():break
        al&=~rm
    # drop specks
    lab,n=nd.label(al);sz=nd.sum(al,lab,range(1,n+1));al&=np.isin(lab,[i+1 for i,v in enumerate(sz) if v>=12])
    im[:,:,3]=np.where(al,255,0);Image.fromarray(im.astype('uint8')).save(path)
