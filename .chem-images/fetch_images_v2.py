#!/usr/bin/env python3
import re, json, time, random, base64, zlib, html
from io import BytesIO
from pathlib import Path
import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
DATA = json.loads(zlib.decompress(base64.b64decode('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')).decode('utf-8'))
OUT = BASE/'out'
IMGDIR = OUT/'substances'
IMGDIR.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({'User-Agent':'HoaHocAlchemy/1.9.93 educational offline chemistry photo curator; Wikimedia Commons attribution preserved'})
COMMONS='https://commons.wikimedia.org/w/api.php'
WIKI='https://en.wikipedia.org/w/api.php'
BAD_TITLE=['structure','structural','molecule','molecular','ball-and-stick','ball and stick','space-filling','space filling','unit cell','lattice','diagram','scheme','equation','formula','spectrum','spectra','orbital','plot','graph','chart','map','logo','icon','symbol','ghs','hazard','msds','sds','mechanism','3d model','model of','render','lewis','skeletal','geometry','phase diagram']
PHOTO_HINTS=['sample','crystal','crystals','powder','solid','liquid','solution','aqueous','ampoule','ampule','vial','bottle','metal','mineral','precipitate','pellets','granules','reagent','laboratory','lab','element','ore','under oil']
ALLOWED_LICENSE=['cc by','cc-by','cc by-sa','cc-by-sa','cc0','public domain','pd-']
OVERRIDE={'H2O':'water liquid sample','C':'graphite carbon sample','P':'red phosphorus sample','S':'sulfur element sample','Si':'silicon element sample','H2':'hydrogen gas ampoule','O2':'oxygen gas ampoule','N2':'nitrogen gas ampoule','F2':'fluorine ampoule','Cl2':'chlorine gas ampoule','Br2':'bromine liquid ampoule','CO2':'dry ice carbon dioxide','SO2':'sulfur dioxide ampoule','NO':'nitric oxide gas ampoule','NO2':'nitrogen dioxide ampoule','N2O':'nitrous oxide gas sample','NH3':'ammonia ampoule','H2S':'hydrogen sulfide gas sample','PH3':'phosphine gas sample','SiF4':'silicon tetrafluoride sample','HCl':'hydrochloric acid solution laboratory','HF':'hydrofluoric acid laboratory bottle','H2SO4l':'sulfuric acid solution laboratory','H2SO4c':'concentrated sulfuric acid laboratory','HNO3l':'nitric acid solution laboratory','HNO3c':'concentrated nitric acid laboratory','H2CO3':'carbonated water carbonic acid','H2SO3':'sulfurous acid solution','HClO':'hypochlorous acid solution','HBrO':'hypobromous acid solution','NaOH':'sodium hydroxide pellets','KOH':'potassium hydroxide pellets','Ca(OH)2':'calcium hydroxide powder','Ba(OH)2':'barium hydroxide crystals','H2O2':'hydrogen peroxide solution laboratory'}

def strip_tags(v): return re.sub(r'<[^>]+>',' ',html.unescape(v or '')).strip()
def norm(v): return re.sub(r'[^a-z0-9]+',' ',(v or '').lower()).strip()
def compact(v): return re.sub(r'[^a-z0-9]+','',(v or '').lower())
def clean_name(n): return re.sub(r'\s+',' ',re.sub(r'\s*\([^)]*\)\s*',' ',n or '')).strip()
def formula_clean(f): return (f or '').replace(' (l)','').replace(' (đ)','').replace('(l)','').replace('(đ)','').strip()
def safe_file(v): return re.sub(r'[^A-Za-z0-9_.()-]+','_',v)

def get(url,params=None,timeout=35,binary=False):
    last=None
    for attempt in range(7):
        try:
            r=S.get(url,params=params,timeout=timeout)
            if r.status_code in (429,500,502,503,504):
                last=RuntimeError(f'HTTP {r.status_code}'); time.sleep(min(18,1.2*(2**attempt))+random.random()); continue
            r.raise_for_status(); return r.content if binary else r
        except Exception as e:
            last=e; time.sleep(min(12,.8*(2**attempt))+random.random()*.4)
    raise last or RuntimeError('request failed')

def wiki_title(x):
    n=clean_name(x['n']); q=(f'"{n}" chemical element' if x['c']=='kl' else f'"{n}" chemical compound') if n and n.lower()!='nước' else f'"{formula_clean(x["f"])}" chemical compound'
    try:
        p={'action':'query','list':'search','srsearch':q,'srlimit':3,'srnamespace':0,'format':'json','formatversion':2,'origin':'*'}
        for a in get(WIKI,p).json().get('query',{}).get('search',[]):
            t=a.get('title',''); sn=norm(strip_tags(a.get('snippet','')))
            if any(z in sn for z in ['chemical','compound','element','acid','oxide','salt','hydroxide','gas']): return t
    except Exception: pass
    return None

def search_commons(q,limit=14):
    p={'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':limit,'prop':'imageinfo','iiprop':'url|mime|size|extmetadata','iiurlwidth':560,'format':'json','formatversion':2,'origin':'*'}
    return get(COMMONS,p).json().get('query',{}).get('pages',[]) or []
def ev(p,k):
    try:return p['imageinfo'][0].get('extmetadata',{}).get(k,{}).get('value','') or ''
    except:return ''
def license_ok(p):
    lic=(ev(p,'LicenseShortName')+' '+ev(p,'UsageTerms')).lower(); return any(z in lic for z in ALLOWED_LICENSE)

def score(x,p):
    ii=(p.get('imageinfo') or [{}])[0]; mime=ii.get('mime','')
    if mime not in ('image/jpeg','image/png','image/webp','image/tiff') or not license_ok(p): return -9999
    title=p.get('title',''); t=norm(re.sub(r'^file:','',title,flags=re.I)); desc=norm(strip_tags(ev(p,'ImageDescription'))+' '+strip_tags(ev(p,'ObjectName')))
    n=norm(clean_name(x['n'])); n='water' if n=='n c' else n; f=compact(formula_clean(x['f'])); sc=0
    if n and n in t: sc+=150
    elif n:
        words=[w for w in n.split() if len(w)>=3]; hit=sum(w in t for w in words)
        if words and hit==len(words): sc+=95
        elif words: sc+=16*hit
    if f and len(f)>=2:
        tc=compact(t); dc=compact(desc)
        if f in tc: sc+=70
        elif f in dc: sc+=28
    for z in PHOTO_HINTS:
        if z in t: sc+=10
        elif z in desc: sc+=3
    for z in BAD_TITLE:
        if z in t: sc-=160
        elif z in desc: sc-=25
    if any(z in t for z in ['factory','mining','portrait','museum building','location map']): sc-=55
    w,h=ii.get('width',0),ii.get('height',0)
    if w>=450 and h>=300: sc+=8
    if w<180 or h<140: sc-=30
    return sc

def cand(x,p,q,sc):
    ii=p['imageinfo'][0]; lic=ev(p,'LicenseShortName') or ev(p,'UsageTerms')
    return {'title':p.get('title',''),'query':q,'score':sc,'thumb_url':ii.get('thumburl') or ii.get('url'),'original_url':ii.get('url'),'page_url':ii.get('descriptionurl') or ('https://commons.wikimedia.org/wiki/'+p.get('title','').replace(' ','_')),'mime':ii.get('mime',''),'width':ii.get('width'),'height':ii.get('height'),'author':strip_tags(ev(p,'Artist')),'license':strip_tags(lic),'license_url':ev(p,'LicenseUrl'),'credit':strip_tags(ev(p,'Credit')),'description':strip_tags(ev(p,'ImageDescription'))}

def queries_for(x):
    n=clean_name(x['n']); n='water' if n.lower()=='nước' else n; f=formula_clean(x['f']); qs=[]
    if x['id'] in OVERRIDE: qs.append(OVERRIDE[x['id']])
    if n:
        qs += [f'"{n}" sample',f'"{n}" chemical']
        if x['s']=='r': qs.append(f'"{n}" crystals powder')
        elif x['s']=='l': qs.append(f'"{n}" liquid ampoule')
        elif x['s']=='k': qs.append(f'"{n}" gas ampoule')
        elif x['s']=='dd': qs.append(f'"{n}" solution crystals')
    wt=wiki_title(x)
    if wt and norm(wt)!=norm(n): qs += [f'"{wt}" sample',f'"{wt}" chemical']
    if f: qs.append(f'"{f}" chemical sample')
    out=[]
    for q in qs:
        if q not in out: out.append(q)
    return out[:6]

def choose(x):
    pool={}
    for q in queries_for(x):
        try: pages=search_commons(q)
        except Exception as e: print('SEARCH_ERR',x['id'],q,e,flush=True); continue
        for p in pages:
            try:
                sc=score(x,p)
                if sc>-9000:
                    c=cand(x,p,q,sc); old=pool.get(c['title'])
                    if old is None or sc>old['score']: pool[c['title']]=c
            except Exception: pass
        if pool and max(v['score'] for v in pool.values())>=168: break
        time.sleep(.12)
    arr=sorted(pool.values(),key=lambda c:c['score'],reverse=True); return (arr[0] if arr else None),arr[:8]

def save_image(x,c):
    raw=get(c['thumb_url'],timeout=50,binary=True); im=ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert('RGB'); im.thumbnail((560,560),Image.Resampling.LANCZOS)
    fn=safe_file(x['id'])+'.webp'; im.save(IMGDIR/fn,'WEBP',quality=76,method=6); return fn,list(im.size)
def classify(x,c):
    h=norm(c['title']+' '+c.get('description','')); rep='sample'
    if 'solution' in h or 'aqueous' in h: rep='solution'
    elif x['s']=='k' and ('ampoule' in h or 'ampule' in h): rep='gas_ampoule'
    elif x['s']=='k': rep='gas_reference'
    if any(z in h for z in ['hydrate','monohydrate','dihydrate','trihydrate','tetrahydrate','pentahydrate','hexahydrate','heptahydrate','decahydrate']): rep='representative_hydrate'
    return rep

manifest={}; candidates={}; failures=[]
for i,x in enumerate(DATA,1):
    print(f'[{i}/{len(DATA)}] {x["id"]} {x["n"]}',flush=True); c,top=choose(x); candidates[x['id']]=top
    if not c or c['score']<70:
        failures.append({'id':x['id'],'name':x['n'],'formula':x['f'],'best':c}); manifest[x['id']]={'file':None,'status':'unverified','source':c}; continue
    try: fn,size=save_image(x,c)
    except Exception as e:
        failures.append({'id':x['id'],'name':x['n'],'formula':x['f'],'best':c,'download_error':str(e)}); manifest[x['id']]={'file':None,'status':'download_error','source':c}; continue
    manifest[x['id']]={'file':'substances/'+fn,'status':'verified_candidate','representation':classify(x,c),'score':c['score'],'source_page':c['page_url'],'original_url':c['original_url'],'author':c['author'],'license':c['license'],'license_url':c['license_url'],'commons_title':c['title'],'size':size,'query':c['query']}; time.sleep(.08)

OUT.mkdir(parents=True,exist_ok=True)
(OUT/'substance-images.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf-8')
(OUT/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),'utf-8')
(OUT/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),'utf-8')
(OUT/'substance-images.js').write_text('const SUBSTANCE_IMAGES = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
lines=['HoaHocAlchemy v1.9.93 - real substance image credits','Source: Wikimedia Commons','Only free-license/Public Domain candidates selected by this build.','']
for x in DATA:
    e=manifest[x['id']]
    if e.get('file'): lines += [f"{x['id']} | {x['n']} | {x['f']}",f"  File: {e.get('commons_title','')}",f"  Author: {e.get('author','')}",f"  License: {e.get('license','')}",f"  Source: {e.get('source_page','')}",'']
    else: lines += [f"{x['id']} | {x['n']} | {x['f']} | NO VERIFIED FREE PHOTO EMBEDDED",'']
(OUT/'IMAGE-CREDITS.txt').write_text('\n'.join(lines),'utf-8')
try:
    font=ImageFont.load_default(); chunk=48; cw,ch=190,150; cols=6; rows=8
    for page,start in enumerate(range(0,len(DATA),chunk),1):
        sheet=Image.new('RGB',(cols*cw,rows*ch),(245,245,245)); d=ImageDraw.Draw(sheet)
        for j,x in enumerate(DATA[start:start+chunk]):
            rr=j//cols; cc=j%cols; xx=cc*cw; yy=rr*ch; e=manifest.get(x['id'],{}); fp=OUT/str(e.get('file',''))
            if e.get('file') and fp.exists():
                im=Image.open(fp).convert('RGB'); im.thumbnail((180,112),Image.Resampling.LANCZOS); sheet.paste(im,(xx+5+(180-im.width)//2,yy+3+(112-im.height)//2))
            else:
                d.rectangle((xx+5,yy+3,xx+185,yy+115),outline=(120,120,120)); d.text((xx+30,yy+48),'NO VERIFIED PHOTO',fill=(80,80,80),font=font)
            d.text((xx+5,yy+118),f"{x['id']} | {x['f']}",fill=(0,0,0),font=font); d.text((xx+5,yy+132),f"score {e.get('score','-')}",fill=(40,40,40),font=font)
        sheet.save(OUT/f'contact-{page:02d}.jpg','JPEG',quality=78,optimize=True)
except Exception as e: print('CONTACT_SHEET_ERR',e,flush=True)
print('DONE',len(manifest),'embedded',sum(bool(v.get('file')) for v in manifest.values()),'failures',len(failures),flush=True)
