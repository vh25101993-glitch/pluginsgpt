#!/usr/bin/env python3
import re,json,zlib,base64,time,random,html,threading
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor,as_completed
import requests
from PIL import Image,ImageOps
BASE=Path(__file__).resolve().parent; OUT=BASE/'out-v3'; IMG=OUT/'substances'; IMG.mkdir(parents=True,exist_ok=True)
src=(BASE/'fetch_images_v2.py').read_text('utf-8'); m=re.search(r"base64\.b64decode\('([^']+)'\)",src); DATA=json.loads(zlib.decompress(base64.b64decode(m.group(1))).decode('utf-8'))
API='https://commons.wikimedia.org/w/api.php'; BAD=['structure','structural','molecule','ball-and-stick','space-filling','unit cell','diagram','scheme','equation','formula','spectrum','orbital','plot','graph','chart','map','logo','icon','ghs','hazard','mechanism','3d model','render','lewis','skeletal','geometry','phase diagram']; HINT=['sample','crystal','crystals','powder','solid','liquid','solution','aqueous','ampoule','ampule','vial','bottle','metal','mineral','precipitate','pellets','granules','reagent','laboratory','element','under oil']; ALLOW=['cc by','cc-by','cc by-sa','cc-by-sa','cc0','public domain','pd-']; TL=threading.local()
def sess():
 if not hasattr(TL,'s'): TL.s=requests.Session(); TL.s.headers['User-Agent']='HoaHocAlchemy/1.9.93 educational offline photo curator; Wikimedia attribution retained'
 return TL.s
def req(url,params=None,binary=False):
 last=RuntimeError('request failed')
 for a in range(6):
  try:
   r=sess().get(url,params=params,timeout=35)
   if r.status_code in (429,500,502,503,504): last=RuntimeError(f'HTTP {r.status_code}'); time.sleep(min(8,.7*2**a)+random.random()); continue
   r.raise_for_status(); return r.content if binary else r
  except Exception as e: last=e; time.sleep(min(6,.5*2**a)+random.random()*.3)
 raise last
def strip(v): return re.sub(r'<[^>]+>',' ',html.unescape(v or '')).strip()
def norm(v): return re.sub(r'[^a-z0-9]+',' ',(v or '').lower()).strip()
def comp(v): return re.sub(r'[^a-z0-9]+','',(v or '').lower())
def ev(p,k):
 try:return p['imageinfo'][0].get('extmetadata',{}).get(k,{}).get('value','') or ''
 except:return ''
def clean_name(x):
 n=x['n'].replace(' (loãng)','').replace(' (đặc)','').replace('(loãng)','').replace('(đặc)','').strip()
 return 'water' if n.lower()=='nước' else n
def license_ok(p):
 s=(ev(p,'LicenseShortName')+' '+ev(p,'UsageTerms')).lower(); return any(a in s for a in ALLOW)
def search(q):
 p={'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':12,'prop':'imageinfo','iiprop':'url|mime|size|extmetadata','iiurlwidth':520,'format':'json','formatversion':2,'origin':'*'}
 return req(API,p).json().get('query',{}).get('pages',[]) or []
def score(x,p):
 ii=(p.get('imageinfo') or [{}])[0]
 if ii.get('mime') not in ('image/jpeg','image/png','image/webp','image/tiff') or not license_ok(p): return -9999
 t=norm(re.sub(r'^file:','',p.get('title',''),flags=re.I)); d=norm(strip(ev(p,'ImageDescription'))+' '+strip(ev(p,'ObjectName'))); n=norm(clean_name(x)); f=comp(x['f'].replace('(l)','').replace('(đ)',''))
 sc=0
 if n and n in t: sc+=170
 else:
  w=[z for z in n.split() if len(z)>=2]; hit=sum(z in t for z in w); sc+=22*hit
 if f and len(f)>=2:
  if f in comp(t): sc+=85
  elif f in comp(d): sc+=35
 for z in HINT:
  if z in t: sc+=9
 for z in BAD:
  if z in t: sc-=220
 if any(z in t for z in ['factory','mining','portrait','location map']): sc-=70
 if ii.get('width',0)>=400 and ii.get('height',0)>=250: sc+=5
 return sc
def candidate(x,p,q,sc):
 ii=p['imageinfo'][0]; lic=strip(ev(p,'LicenseShortName') or ev(p,'UsageTerms'))
 return {'title':p.get('title',''),'query':q,'score':sc,'thumb_url':ii.get('thumburl') or ii.get('url'),'original_url':ii.get('url'),'page_url':ii.get('descriptionurl') or ('https://commons.wikimedia.org/wiki/'+p.get('title','').replace(' ','_')),'author':strip(ev(p,'Artist')),'license':lic,'license_url':ev(p,'LicenseUrl'),'description':strip(ev(p,'ImageDescription'))}
def find_one(x):
 n=clean_name(x); f=x['f'].replace('(l)','').replace('(đ)','').strip(); qs=[f'"{n}" sample',f'"{n}"']
 if f and norm(f)!=norm(n): qs.append(f'"{f}" sample')
 pool={}
 for q in qs:
  try: pages=search(q)
  except Exception: continue
  for p in pages:
   try:
    sc=score(x,p)
    if sc>-9000:
     c=candidate(x,p,q,sc); old=pool.get(c['title']);
     if old is None or sc>old['score']: pool[c['title']]=c
   except: pass
  if pool and max(v['score'] for v in pool.values())>=175: break
 arr=sorted(pool.values(),key=lambda c:c['score'],reverse=True); return x,(arr[0] if arr else None),arr[:5]
def save_one(x,c):
 if not c or c['score']<90:return x['id'],None
 try:
  raw=req(c['thumb_url'],binary=True); im=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert('RGB'); im.thumbnail((520,520),Image.Resampling.LANCZOS); fn=re.sub(r'[^A-Za-z0-9_.()-]+','_',x['id'])+'.webp'; im.save(IMG/fn,'WEBP',quality=76,method=6)
  h=norm(c['title']+' '+c.get('description','')); rep='solution' if ('solution' in h or 'aqueous' in h) else ('gas_ampoule' if x['s']=='k' and ('ampoule' in h or 'ampule' in h) else ('gas_reference' if x['s']=='k' else 'sample'))
  if any(z in h for z in ['hydrate','monohydrate','dihydrate','trihydrate','tetrahydrate','pentahydrate','hexahydrate','heptahydrate','decahydrate']):rep='representative_hydrate'
  return x['id'],{'file':'substances/'+fn,'status':'verified_candidate','representation':rep,'score':c['score'],'source_page':c['page_url'],'original_url':c['original_url'],'author':c['author'],'license':c['license'],'license_url':c['license_url'],'commons_title':c['title'],'size':list(im.size),'query':c['query']}
 except Exception as e:return x['id'],{'file':None,'status':'download_error','error':str(e),'source':c}

found={}; tops={}
with ThreadPoolExecutor(max_workers=6) as ex:
 fut={ex.submit(find_one,x):x for x in DATA}
 done=0
 for f in as_completed(fut):
  x,c,top=f.result(); found[x['id']]=(x,c); tops[x['id']]=top; done+=1
  if done%25==0: print('SEARCHED',done,'/',len(DATA),flush=True)
manifest={}
with ThreadPoolExecutor(max_workers=5) as ex:
 fut={ex.submit(save_one,x,c):sid for sid,(x,c) in found.items()}
 done=0
 for f in as_completed(fut):
  sid,e=f.result(); manifest[sid]=e or {'file':None,'status':'unverified'}; done+=1
  if done%25==0: print('DOWNLOADED',done,'/',len(DATA),flush=True)
# restore stable database order
manifest={x['id']:manifest.get(x['id'],{'file':None,'status':'unverified'}) for x in DATA}
OUT.mkdir(parents=True,exist_ok=True); (OUT/'substance-images.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf-8'); (OUT/'candidates.json').write_text(json.dumps(tops,ensure_ascii=False,indent=2),'utf-8'); (OUT/'substance-images.js').write_text('const SUBSTANCE_IMAGES = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
print('DONE',len(DATA),'embedded',sum(bool(v.get('file')) for v in manifest.values()),flush=True)
