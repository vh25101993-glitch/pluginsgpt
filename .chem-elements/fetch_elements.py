#!/usr/bin/env python3
import json,re,time,random
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parent; OUT=BASE/'out'; IMG=OUT/'substances'; IMG.mkdir(parents=True,exist_ok=True)
URL='https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json'
MAP={'Na':'Sodium','K':'Potassium','Ca':'Calcium','Mg':'Magnesium','Al':'Aluminium','Zn':'Zinc','Fe':'Iron','Cu':'Copper','Ag':'Silver','Ba':'Barium','Si':'Silicon','H2':'Hydrogen','O2':'Oxygen','F2':'Fluorine','Cl2':'Chlorine','Br2':'Bromine','S':'Sulfur','C':'Carbon','N2':'Nitrogen','P':'Phosphorus'}
S=requests.Session(); S.headers['User-Agent']='HoaHocAlchemy/1.9.93 educational element image curator'
def get(u):
  last=None
  for a in range(6):
    try:
      r=S.get(u,timeout=45)
      if r.status_code in (429,500,502,503,504): time.sleep(min(12,2**a)+random.random()); continue
      r.raise_for_status(); return r
    except Exception as e: last=e; time.sleep(min(10,1.2*2**a))
  raise last
D=get(URL).json(); els={e['name']:e for e in D['elements']}; man={}
for i,(sid,name) in enumerate(MAP.items(),1):
  print(i,sid,name,flush=True); e=els[name]; im=e.get('image') or {}; u=im.get('url'); attr=im.get('attribution','')
  if not u: man[sid]={'file':None,'status':'missing'}; continue
  raw=get(u).content; pic=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert('RGB'); pic.thumbnail((560,560),Image.Resampling.LANCZOS); fn=re.sub(r'[^A-Za-z0-9_.()-]+','_',sid)+'.webp'; pic.save(IMG/fn,'WEBP',quality=78,method=6)
  lic='CC BY 3.0' if 'CC BY 3.0' in attr else ('CC BY-SA 3.0' if 'CC BY-SA 3.0' in attr else 'See attribution')
  m=re.search(r'source:\s*(https?://[^ >]+)',attr); source=m.group(1) if m else e.get('source','')
  author=attr.split(',')[0].strip() if attr else ''
  man[sid]={'file':'substances/'+fn,'status':'curated_element_photo','representation':'element_sample','source_page':source,'original_url':u,'author':author,'license':lic,'license_url':'https://creativecommons.org/licenses/by/3.0/' if lic=='CC BY 3.0' else '', 'commons_title':im.get('title',''),'attribution':attr,'size':list(pic.size)}
  time.sleep(.08)
(OUT/'element-images.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),'utf-8')
try:
  font=ImageFont.load_default(); cw,ch=220,165; cols=5; rows=4; sheet=Image.new('RGB',(cols*cw,rows*ch),(245,245,245)); d=ImageDraw.Draw(sheet)
  for j,(sid,name) in enumerate(MAP.items()):
    x=(j%cols)*cw; y=(j//cols)*ch; fp=OUT/man[sid]['file']; p=Image.open(fp).convert('RGB'); p.thumbnail((208,125),Image.Resampling.LANCZOS); sheet.paste(p,(x+6+(208-p.width)//2,y+4+(125-p.height)//2)); d.text((x+7,y+132),f'{sid} | {name}',fill=(0,0,0),font=font)
  sheet.save(OUT/'element-contact.jpg','JPEG',quality=82,optimize=True)
except Exception as e: print('SHEET_ERR',e)
print('DONE',len(man),flush=True)
