import json,io,base64,random
from PIL import Image, ImageOps
A='assets/buildings/';P='assets/props/';T='assets/trees/';B='assets/bushes/';L='assets/life/';V='assets/village2/';D='assets/decorations/';G='assets/ground/';C='assets/canal/'
# (key,file,cx,base,width,flip)
S=[('tea_house',A+'tea_house.png',132,132,165,0),('calli',A+'calligrapher.png',320,112,120,0),('back_house',V+'farmhouse_porch.png',322,76,92,0),
('shop1',A+'house_plain.png',490,62,84,0),('shop2',A+'house_plain.png',575,62,84,0),
('stall_r',A+'stall_red.png',478,114,50,0),('stall_b',A+'stall_blue.png',532,114,46,0),('stall_t',A+'stall_tan.png',586,114,50,0),
('home',A+'home.png',125,322,140,0),('granny',A+'granny_house.png',556,320,200,0),
('ls1',P+'lantern_string.png',277,242,60,0),('ls2',P+'lantern_string.png',413,242,60,0),('ls3',P+'lantern_string.png',318,358,136,0),
('board',P+'notice_board.png',344,262,50,0),('well',P+'well.png',283,304,32,0),('sundial',P+'sundial.png',362,302,15,0),
('lion1',P+'stone_lion.png',100,138,12,0),('lion2',P+'stone_lion.png',164,138,12,1),
('shrine',V+'roadside_shrine.png',40,128,26,0),('incense',D+'incense_burner.png',40,140,10,0),('stonelant',D+'stone_lantern.png',364,120,10,0),
('lamp1',V+'lamp_post_1.png',392,232,10,0),('lamp2',V+'lamp_post_2.png',452,232,10,0),
('lpole1',D+'lantern_pole.png',96,345,10,0),('lpole2',D+'lantern_pole.png',154,345,10,1),
('bench2',L+'stone_bench.png',300,350,22,0),('steamers',V+'bamboo_steamers.png',214,130,12,0),
# market yard
('barrels',P+'barrels.png',612,70,26,0),('baskets2',L+'basket_stack.png',462,124,12,0),('cart',V+'handcart.png',588,146,26,0),
# home yard: everything against the walls
('wash',L+'washing_line.png',212,268,30,0),('wood',L+'firewood.png',44,304,18,0),('jar1',L+'water_jar.png',196,304,11,0),
# granny yard
('fence1',L+'fence_straight.png',466,262,26,0),('jar2',L+'water_jar_lid.png',642-38,300,10,0),('fbed1',V+'flower_bed_1.png',478,348,34,0),
# back house yard

# --- greenery: willows ONLY on the canal, framing the square
('cw1',P+'willow.png',282,226,62,0),('cw2',P+'willow.png',356,226,62,1),('cw3',P+'willow.png',62,262,66,1),('cw4',P+'willow.png',592,252,62,0),
# background band: dark camphors/bamboo behind buildings, one accent tree per landmark
('bg1',T+'camphor.png',24,66,48,0),('bg2',T+'camphor_2.png',252,30,40,0),('bg3',T+'bamboo.png',236,52,18,0),('bg4',T+'bamboo.png',414,44,16,1),
('acc_plum',T+'plum_blossom.png',214,62,40,0),('acc_maple',T+'maple.png',398,62,44,0),
# foreground corners frame the view
('fg1',T+'camphor.png',40,374,64,0),('fg2',T+'pine.png',190,374,48,0),('fg4',T+'camphor_2.png',626,400,58,1),
# edges
('edgeL1',T+'bamboo.png',10,246,18,0),('edgeL2',T+'bamboo.png',24,240,14,1),('edgeR',T+'plum_blossom.png',632,212,32,1),
# shrubs: symmetric pairs at entrances
('sqL',B+'azalea.png',254,258,16,0),('sqR',B+'azalea.png',436,258,16,1),
('reedL1',B+'reeds.png',6,176,12,0),('reedL2',B+'reeds.png',16,182,9,1),('reedR1',B+'reeds.png',630,200,12,0),('reedR2',B+'reeds.png',620,206,9,1),
('fernL',B+'fern.png',20,254,12,0),
('apples','assets/props2/apple_crate.png',441,122,22,0),('umbrella','assets/props2/oil_umbrella.png',602,336,22,0),('teatray','assets/props2/tea_tray.png',192,140,18,0),('jars3','assets/props2/clay_jars.png',448,304,16,1),('oar','assets/props2/oar_rope.png',76,212,18,0),
('top1',P+'willow.png',18,40,46,0),('top2',T+'camphor.png',62,22,42,1),('top3',P+'willow.png',204,26,40,1),('top4',T+'willow_tall.png',268,34,34,0),
('top5',T+'camphor_2.png',372,24,38,0),('top6',P+'willow.png',438,40,40,1),('top7',T+'camphor.png',636,40,40,1),('top8',T+'willow_tall.png',620,18,30,0),
('left1',T+'camphor.png',6,118,40,0),('left2',T+'camphor_2.png',8,346,46,1),('left3',P+'willow.png',8,300,40,0),
('bot1',P+'willow.png',244,384,56,1),('bot2',P+'willow.png',418,386,52,0),('bot3',T+'willow_young.png',112,390,44,1),('bot4',P+'willow.png',570,392,50,0),
('nb1',P+'willow.png',626,158,40,1),('nb2',P+'willow.png',228,160,36,0),
('right1',T+'camphor.png',638,268,38,1)]
s=open('index.html').read();a=s.index('const OBJS=');e=s.index(';\n',a)
cache={};objs=[]
for k,f,cx,base,w,fl in S:
    key=(f,w,fl)
    im=Image.open(f).convert('RGBA');h=round(im.height*w/im.width)
    if key not in cache:
        r=im.resize((w,h),Image.LANCZOS)
        if fl:r=ImageOps.mirror(r)
        b=io.BytesIO();r.save(b,'PNG',optimize=True);cache[key]='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
    o={'k':k,'x':round(cx-w/2),'y':base-h,'w':w,'h':h,'base':base,'src':cache[key]}
    objs.append(o)
for x in (113,151):
    im=Image.open(D+('banner_left.png' if x<130 else 'banner_right.png')).convert('RGBA');h=round(im.height*6/im.width);r=im.resize((6,h),Image.LANCZOS)
    b=io.BytesIO();r.save(b,'PNG');objs.append({'k':'ban'+str(x),'x':x-3,'y':96,'w':6,'h':h,'base':133,'src':'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()})
s=s[:a]+'const OBJS='+json.dumps(objs)+s[e:]
# --- lantern glows: find red lantern blobs inside lantern-bearing objects
import numpy as np, scipy.ndimage as nd, re
LIT=('tea_house','ls1','ls2','ls3','lpole1','lpole2')
pts=[]
for k,f,cx,b0,w,fl in S:
    if k not in LIT:continue
    im=Image.open(f).convert('RGBA');h=round(im.height*w/im.width)
    a=np.array(im).astype(int);red=(a[:,:,0]>150)&(a[:,:,1]<110)&(a[:,:,2]<100)&(a[:,:,3]>0)
    lab,n=nd.label(red);sizes=nd.sum(red,lab,range(1,n+1))
    for i,c in enumerate(nd.center_of_mass(red,lab,range(1,n+1))):
        if sizes[i]<0.002*red.size:continue
        yy,xx=c;x=xx*w/im.width
        if fl:x=w-x
        pts.append([round(cx-w/2+x),round(b0-h+yy*h/im.height)])
lit='['+','.join('[%d,%d]'%(x,y) for x,y in pts)+']'
s=re.sub(r"\[\[[0-9,\[\]]+\]\]\.forEach\(p=>LANT\.push\(p\)\);",lambda m:lit+'.forEach(p=>LANT.push(p));',s,count=1)
print('glows',len(pts))

# ground: clustered details only
base=Image.open('assets/map/ground_base.png').convert('RGBA').resize((640,360),Image.LANCZOS)
random.seed(3)
def put(nm,x,y,w,src=G):
    im=Image.open(src+nm+'.png').convert('RGBA');h=max(3,round(im.height*w/im.width));base.alpha_composite(im.resize((w,h),Image.LANCZOS),(round(x-w/2),round(y-h)))
# tree-base clusters: grass + moss/clover hugging each trunk
for k,f,cx,b,w,fl in S:
    if k.startswith(('cw','bg1','fg','edge','acc')):
        for dx in (-w*0.28,w*0.26):put(random.choice(['grass_tuft_1','grass_tuft_2','clover']),cx+dx,b+2,9)
        if k.startswith(('fg','edge')):put('moss',cx+random.choice([-6,6]),b+5,11)
# flowers grouped by colour in drifts beside paths
for x,y in [(82,252),(90,256),(76,258)]:put('white_flowers',x,y,9)
for x,y in [(228,330),(236,334),(222,336)]:put('purple_flowers',x,y,9)
for x,y in [(456,330),(464,334),(450,336)]:put('yellow_flowers',x,y,9)
for x,y in [(410,90),(418,94)]:put('wildflowers',x,y,10)
for x,y in [(160,62),(168,66)]:put('white_flowers',x,y,8)
# fence lines and wall bases: dry grass and rocks
for x in (458,468,476):put('dry_grass',x,266,9)
for x,y in [(6,138),(56,140)]:put('rocks',x,y,8)
for x,y in [(632,150),(600,150)]:put('rocks',x,y,7)
put('fallen_leaves',400,72,10);put('fallen_leaves',204,74,9)
# canal life in two calm groups
put('lily_pads_lotus',186,206,24,C);put('lily_pads_lotus',214,212,14,C);put('lily_pads_lotus',536,200,22,C);put('lily_pads_lotus',512,206,13,C)
put('rowing_boat',488,214,30,C)
bb=io.BytesIO();base.convert('RGB').save(bb,'PNG',optimize=True)
gu='data:image/png;base64,'+base64.b64encode(bb.getvalue()).decode()
k='const MAPIMG=new Image();MAPIMG.src="';i=s.index(k)+len(k);j=s.index('"',i);s=s[:i]+gu+s[j:]
open('index.html','w').write(s);print(len(objs))
