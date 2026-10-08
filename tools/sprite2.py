import sys,numpy as np
from PIL import Image
src,pre,boxes=sys.argv[1],sys.argv[2],eval(sys.argv[3])
im=Image.open(src).convert('RGBA');a=np.array(im).astype(int)
bgc=a[5,5,:3];print('bg',bgc)
bg=(np.abs(a[:,:,:3]-bgc).max(axis=2)<12);a[bg,3]=0;im=Image.fromarray(a.astype('uint8'))
import scipy.ndimage as nd
def main(c):
    al=np.array(c)[:,:,3]>0;lab,n=nd.label(nd.binary_dilation(al,iterations=3))
    if n>1:
        sz=nd.sum(al,lab,range(1,n+1));keep=np.isin(lab,[i+1 for i,v in enumerate(sz) if v>=0.005*sz.max()])&al
        x=np.array(c);x[~keep,3]=0;c=Image.fromarray(x)
    return c.crop(c.getbbox())
crops={k:main(im.crop(b)) for k,b in boxes.items()}
_old={k:im.crop(b).crop(im.crop(b).getbbox()) for k,b in boxes.items()}
# shared adaptive palette
strip=Image.new('RGB',(sum(c.width for c in crops.values()),max(c.height for c in crops.values())),tuple(int(v) for v in bgc))
x=0
for c in crops.values(): strip.paste(c,(x,0),c);x+=c.width
pal=strip.quantize(colors=16,method=Image.MEDIANCUT)
M=max(max(c.size) for c in crops.values())
def make(c,size):
    w,h=c.size;s=size/M;c=c.resize((max(1,round(w*s)),max(1,round(h*s))),Image.BOX)
    q=np.array(c.convert('RGB').quantize(palette=pal,dither=0).convert('RGBA'));q[:,:,3]=np.where(np.array(c)[:,:,3]>110,255,0)
    out=Image.new('RGBA',(size,size),(0,0,0,0));sp=Image.fromarray(q);out.paste(sp,((size-sp.width)//2,size-sp.height),sp);return out
sheet=Image.new('RGBA',(32*len(crops),32))
for i,(k,c) in enumerate(crops.items()):
    sheet.paste(make(c,32),(i*32,0));make(c,22).save(f'{pre}_{k}_22.png')
sheet.save(f'{pre}_sheet_32.png');sheet.resize((sheet.width*8,256),Image.NEAREST).save(f'{pre}_sheet_preview.png')
