import numpy as np,base64,io,json
from PIL import Image
im=Image.open('player_concept.png').convert('RGBA');a=np.array(im).astype(int)
bgc=a[5,5,:3];bg=np.abs(a[:,:,:3]-bgc).max(axis=2)<14;a[bg,3]=0;im=Image.fromarray(a.astype('uint8'))
B={'front':(60,25,195,265),'back':(315,25,450,265),'right':(575,25,705,265),'w1':(60,295,195,535),'w2':(320,295,450,535),'w3':(575,295,705,535),'w4':(830,295,965,535)}
cr={k:im.crop(b).crop(im.crop(b).getbbox()) for k,b in B.items()}
H=28;M=max(c.height for c in cr.values());W=24
strip=Image.new('RGB',(sum(c.width for c in cr.values()),M),tuple(int(v) for v in bgc));x=0
for c in cr.values():strip.paste(c,(x,0),c);x+=c.width
pal=strip.quantize(colors=16,method=Image.MEDIANCUT)
out={};sheet=Image.new('RGBA',(W*len(cr),H))
for i,(k,c) in enumerate(cr.items()):
    s=H/M;c2=c.resize((max(1,round(c.width*s)),max(1,round(c.height*s))),Image.BOX)
    q=np.array(c2.convert('RGB').quantize(palette=pal,dither=0).convert('RGBA'));q[:,:,3]=np.where(np.array(c2)[:,:,3]>110,255,0)
    f=Image.new('RGBA',(W,H));sp=Image.fromarray(q);f.paste(sp,((W-sp.width)//2,H-sp.height),sp);sheet.paste(f,(i*W,0))
    b=io.BytesIO();f.save(b,'PNG');out[k]='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
sheet.save('player_sheet.png');sheet.resize((sheet.width*8,H*8),Image.NEAREST).save('player_sheet_preview.png')
json.dump(out,open('/tmp/claude-0/player.json','w'))
