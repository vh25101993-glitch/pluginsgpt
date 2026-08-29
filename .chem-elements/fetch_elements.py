#!/usr/bin/env python3
import json,re,time,random,urllib.parse
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont

BASE=Path(__file__).resolve().parent
OUT=BASE/'out'; IMG=OUT/'substances'; IMG.mkdir(parents=True,exist_ok=True)
URL='https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json'
MAP={'Na':'Sodium','K':'Potassium','Ca':'Calcium','Mg':'Magnesium','Al':'Aluminium','Zn':'Zinc','Fe':'Iron','Cu':'Copper','Ag':'Silver','Ba':'Barium','Si':'Silicon','H2':'Hydrogen','O2':'Oxygen','F2':'Fluorine','Cl2':'Chlorine','Br2':'Bromine','S':'Sulfur','C':'Carbon','N2':'Nitrogen','P':'Phosphorus'}
S=requests.Session(); S.headers['User-Agent']='HoaHocAlchemy/1.9.93 educational element image curator; offline use with attribution'

def get(u):
    last=RuntimeError('request failed')
    for a in range(7):
        try:
            r=S.get(u,timeout=45,allow_redirects=True)
            if r.status_code in (429,500,502,503,504):
                last=RuntimeError(f'HTTP {r.status_code} for {u}')
                time.sleep(min(18,1.2*(2**a))+random.random()); continue
            r.raise_for_status(); return r
        except Exception as e:
            last=e; time.sleep(min(12,0.9*(2**a))+random.random()*.5)
    raise last

def thumb_url(original):
    # The dataset points to Wikimedia file URLs. Redirect through Commons and request
    # a small raster rendition, which is more reliable and avoids downloading huge originals.
    fname=urllib.parse.unquote(original.rsplit('/',1)[-1])
    return 'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+urllib.parse.quote(fname,safe='')+'?width=560'

def license_info(attr):
    a=attr or ''
    if 'CC BY-SA 4.0' in a:return 'CC BY-SA 4.0','https://creativecommons.org/licenses/by-sa/4.0/'
    if 'CC BY-SA 3.0' in a:return 'CC BY-SA 3.0','https://creativecommons.org/licenses/by-sa/3.0/'
    if 'CC BY 4.0' in a:return 'CC BY 4.0','https://creativecommons.org/licenses/by/4.0/'
    if 'CC BY 3.0' in a:return 'CC BY 3.0','https://creativecommons.org/licenses/by/3.0/'
    if 'Public domain' in a.lower() or 'public domain' in a.lower():return 'Public Domain',''
    return 'See attribution',''

D=get(URL).json(); els={e['name']:e for e in D['elements']}; man={}; failures=[]
for i,(sid,name) in enumerate(MAP.items(),1):
    print(i,sid,name,flush=True)
    e=els.get(name)
    if not e:
        man[sid]={'file':None,'status':'missing_element_record'}; failures.append([sid,'missing element record']); continue
    im=e.get('image') or {}; u=im.get('url'); attr=im.get('attribution','') or ''
    if not u:
        man[sid]={'file':None,'status':'missing_image'}; failures.append([sid,'missing image URL']); continue
    try:
        r=get(thumb_url(u)); pic=ImageOps.exif_transpose(Image.open(BytesIO(r.content))).convert('RGB')
        pic.thumbnail((560,560),Image.Resampling.LANCZOS)
        fn=re.sub(r'[^A-Za-z0-9_.()-]+','_',sid)+'.webp'; pic.save(IMG/fn,'WEBP',quality=78,method=6)
    except Exception as ex:
        print('DOWNLOAD_ERR',sid,ex,flush=True); man[sid]={'file':None,'status':'download_error','error':str(ex)}; failures.append([sid,str(ex)]); continue
    lic,licurl=license_info(attr)
    m=re.search(r'source:\s*(https?://[^ >]+)',attr,re.I); source=m.group(1) if m else e.get('source','')
    author=attr.split(',')[0].strip() if attr else ''
    man[sid]={'file':'substances/'+fn,'status':'curated_element_photo','representation':'element_sample','source_page':source,'original_url':u,'author':author,'license':lic,'license_url':licurl,'commons_title':im.get('title',''),'attribution':attr,'size':list(pic.size)}
    time.sleep(.12)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'element-images.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),'utf-8')
(OUT/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),'utf-8')
try:
    font=ImageFont.load_default(); cw,ch=220,165; cols=5; rows=4
    sheet=Image.new('RGB',(cols*cw,rows*ch),(245,245,245)); d=ImageDraw.Draw(sheet)
    for j,(sid,name) in enumerate(MAP.items()):
        x=(j%cols)*cw; y=(j//cols)*ch; ent=man.get(sid,{})
        if ent.get('file') and (OUT/ent['file']).exists():
            p=Image.open(OUT/ent['file']).convert('RGB'); p.thumbnail((208,125),Image.Resampling.LANCZOS)
            sheet.paste(p,(x+6+(208-p.width)//2,y+4+(125-p.height)//2))
        else:
            d.rectangle((x+6,y+4,x+214,y+129),outline=(120,120,120)); d.text((x+45,y+55),'NO PHOTO',fill=(80,80,80),font=font)
        d.text((x+7,y+132),f'{sid} | {name}',fill=(0,0,0),font=font)
    sheet.save(OUT/'element-contact.jpg','JPEG',quality=82,optimize=True)
except Exception as e: print('SHEET_ERR',e,flush=True)
print('DONE',len(man),'embedded',sum(bool(v.get('file')) for v in man.values()),'failures',len(failures),flush=True)
