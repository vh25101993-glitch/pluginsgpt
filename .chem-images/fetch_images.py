#!/usr/bin/env python3
import os, re, json, time, math, hashlib
from io import BytesIO
from pathlib import Path
import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
import zlib, base64
DATA = json.loads(zlib.decompress(base64.b64decode('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')).decode('utf-8'))
OUT = BASE/'out'/'substances'
OUT.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({'User-Agent':'HoaHocAlchemy/1.9.93 educational offline app image curator (contact via GitHub)'} )
API='https://commons.wikimedia.org/w/api.php'

NEG = ['structure','structural','molecule','molecular','ball-and-stick','ball and stick','space-filling','space filling','crystal structure','unit cell','lattice','diagram','scheme','equation','formula','spectrum','spectra','orbital','electron','plot','graph','chart','map','logo','icon','symbol','ghs','hazard','msds','sds','mechanism','reaction','3d model','model of','rendering','wikidata','periodic table','lewis','skeletal','geometry','phase diagram']
POS = ['sample','crystal','crystals','powder','solid','liquid','solution','aqueous','ampoule','ampule','vial','bottle','metal','mineral','precipitate','pellets','granules','reagent','laboratory','lab']
OVERRIDE_Q = {'C':'carbon graphite sample','S':'sulfur element sample','P':'red phosphorus sample','Si':'silicon element sample','H2':'hydrogen gas ampoule','O2':'oxygen gas ampoule','F2':'fluorine ampoule','Cl2':'chlorine gas ampoule','N2':'nitrogen liquid gas sample','CO2':'carbon dioxide dry ice','SO2':'sulfur dioxide ampoule','NO2':'nitrogen dioxide gas ampoule','NH3':'ammonia gas ampoule','H2S':'hydrogen sulfide gas ampoule','PH3':'phosphine gas ampoule','SiF4':'silicon tetrafluoride ampoule','HCl':'hydrochloric acid solution laboratory','H2SO4l':'sulfuric acid solution laboratory','H2SO4c':'concentrated sulfuric acid laboratory','HNO3l':'nitric acid solution laboratory','HNO3c':'concentrated nitric acid laboratory','HF':'hydrofluoric acid laboratory bottle','H2CO3':'carbonated water carbonic acid','H2SO3':'sulfurous acid solution','HClO':'hypochlorous acid solution','HBrO':'hypobromous acid solution','NaOH':'sodium hydroxide pellets','KOH':'potassium hydroxide pellets','Ca(OH)2':'calcium hydroxide powder','Ba(OH)2':'barium hydroxide crystals','H2O':'water liquid laboratory','H2O2':'hydrogen peroxide solution laboratory'}
NAME_CLEAN_RE = re.compile(r'\s*\([^)]*\)\s*')
def clean_name(n):
    n=NAME_CLEAN_RE.sub(' ',n).replace('  ',' ').strip()
    for z in ['loãng','đặc','nóng']: n=n.replace(z,'')
    return re.sub(r'\s+',' ',n).strip()
def norm(s): return re.sub(r'[^a-z0-9]+',' ',(s or '').lower()).strip()
def compact(s): return re.sub(r'[^a-z0-9]+','',(s or '').lower())
def make_queries(x):
    if x['id'] in OVERRIDE_Q:return [OVERRIDE_Q[x['id']]]
    n=clean_name(x['n']); f=x['f'].replace('(l)','').replace('(đ)','').strip(); state=x.get('s',''); q=[]
    if state=='r': q += [f'"{n}" sample',f'"{n}" crystals',f'{f} chemical sample']
    elif state=='l': q += [f'"{n}" liquid sample',f'"{n}" ampoule',f'{f} liquid chemical']
    elif state=='k': q += [f'"{n}" gas ampoule',f'"{n}" sample',f'{f} gas chemical']
    else:q += [f'"{n}" chemical sample',f'"{n}" solution',f'"{n}" crystals',f'{f} chemical sample']
    o=[]
    for a in q:
        if a not in o:o.append(a)
    return o
def search_commons(q,limit=12):
    params={'action':'query','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':limit,'prop':'imageinfo','iiprop':'url|mime|size|extmetadata','iiurlwidth':480,'format':'json','formatversion':2,'origin':'*'}
    r=S.get(API,params=params,timeout=30);r.raise_for_status();return r.json().get('query',{}).get('pages',[]) or []
def meta_str(p,key):
    try:return p['imageinfo'][0].get('extmetadata',{}).get(key,{}).get('value','') or ''
    except:return ''
def score_candidate(x,p,q):
    ii=(p.get('imageinfo') or [{}])[0]; mime=ii.get('mime','')
    if mime not in ('image/jpeg','image/png','image/webp'):return -10000
    title=p.get('title','');desc=meta_str(p,'ImageDescription')+' '+meta_str(p,'ObjectName')+' '+meta_str(p,'Categories');hay=norm(title+' '+desc);hcomp=compact(title+' '+desc)
    n=clean_name(x['n']);nwords=[w for w in norm(n).split() if len(w)>=3 and w not in {'acid','oxide','hydroxide','nitrate','sulfate','sulphate','chloride','bromide','iodide','carbonate','phosphate','sulfide','sulphide','solution'}];f=compact(x['f'].replace('(l)','').replace('(đ)',''));s=0
    if norm(n) and norm(n) in hay:s+=60
    s+=sum(8 for w in nwords if w in hay)
    if f and len(f)>=2 and f in hcomp:s+=18
    for z in POS:
        if z in hay:s+=3
    for z in NEG:
        if z in hay:s-=35
    tl=title.lower()
    for z in ['structure','ball','model','diagram','formula','molecule','crystal_structure','unit_cell','spectr','ghs']:
        if z in tl:s-=45
    if x.get('s')=='r' and any(z in hay for z in ['crystal','powder','solid','sample','mineral','pellet']):s+=12
    if x.get('s')=='l' and any(z in hay for z in ['liquid','ampoule','bottle','vial']):s+=12
    if x.get('s')=='k' and any(z in hay for z in ['gas','ampoule','ampule','vial']):s+=12
    if x.get('s')=='dd' and any(z in hay for z in ['solution','aqueous','bottle','reagent','crystal','sample']):s+=7
    w,h=ii.get('width',0),ii.get('height',0)
    if w>=500 and h>=300:s+=5
    if w<200 or h<150:s-=20
    return s
def candidate_data(x,p,q,sc):
    ii=p['imageinfo'][0];em=ii.get('extmetadata',{})
    def ev(k):return em.get(k,{}).get('value','') or ''
    return {'title':p.get('title',''),'query':q,'score':sc,'thumb_url':ii.get('thumburl') or ii.get('url'),'original_url':ii.get('url'),'page_url':ii.get('descriptionurl') or ('https://commons.wikimedia.org/wiki/'+p.get('title','').replace(' ','_')),'mime':ii.get('mime',''),'author':re.sub('<[^>]+>','',ev('Artist')).strip(),'license':ev('LicenseShortName') or ev('UsageTerms'),'license_url':ev('LicenseUrl'),'credit':re.sub('<[^>]+>','',ev('Credit')).strip(),'description':re.sub('<[^>]+>','',ev('ImageDescription')).strip(),'categories':ev('Categories')}
def choose(x):
    allc=[]
    for q in make_queries(x):
        try:pages=search_commons(q)
        except Exception as e:print('SEARCH_ERR',x['id'],q,e,flush=True);continue
        for p in pages:
            try:
                sc=score_candidate(x,p,q)
                if sc>-1000:allc.append(candidate_data(x,p,q,sc))
            except Exception:pass
        if allc and max(c['score'] for c in allc)>=95:break
        time.sleep(.05)
    uniq={}
    for c in allc:
        if c['title'] not in uniq or c['score']>uniq[c['title']]['score']:uniq[c['title']]=c
    arr=sorted(uniq.values(),key=lambda c:c['score'],reverse=True);return (arr[0] if arr else None),arr[:5]
def save_image(x,c):
    r=S.get(c['thumb_url'],timeout=45);r.raise_for_status();im=Image.open(BytesIO(r.content));im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((480,480),Image.Resampling.LANCZOS);fn=re.sub(r'[^A-Za-z0-9_.()-]+','_',x['id'])+'.webp';im.save(OUT/fn,'WEBP',quality=74,method=6);return fn,im.size
def representation(x,c):
    h=norm(c['title']+' '+c.get('description','')+' '+c.get('query',''))
    if x.get('s')=='dd' and ('solution' in h or 'aqueous' in h):return 'solution'
    if x.get('s')=='k' and ('cylinder' in h or 'bottle' in h) and 'ampoul' not in h:return 'container'
    return 'sample'
manifest={};candidates={};failures=[]
for i,x in enumerate(DATA,1):
    print(f'[{i}/{len(DATA)}] {x["id"]} {x["n"]}',flush=True);c,top=choose(x);candidates[x['id']]=top
    if not c or c['score']<38:
        failures.append({'id':x['id'],'name':x['n'],'formula':x['f'],'best':c});manifest[x['id']]={'file':None,'status':'unverified','source':c};continue
    try:fn,size=save_image(x,c)
    except Exception as e:failures.append({'id':x['id'],'name':x['n'],'formula':x['f'],'best':c,'download_error':str(e)});manifest[x['id']]={'file':None,'status':'download_error','source':c};continue
    manifest[x['id']]={'file':'substances/'+fn,'status':'verified_candidate','representation':representation(x,c),'score':c['score'],'source_page':c['page_url'],'original_url':c['original_url'],'author':c['author'],'license':c['license'],'license_url':c['license_url'],'commons_title':c['title'],'size':size,'query':c['query']};time.sleep(.03)
(BASE/'out'/'substance-images.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf-8');(BASE/'out'/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),'utf-8');(BASE/'out'/'failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),'utf-8');(BASE/'out'/'substance-images.js').write_text('const SUBSTANCE_IMAGES = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
try:
    font=ImageFont.load_default();chunk=48;cw,ch=190,150;cols=6;rows=8
    for page,start in enumerate(range(0,len(DATA),chunk),1):
        sheet=Image.new('RGB',(cols*cw,rows*ch),(245,245,245));d=ImageDraw.Draw(sheet)
        for j,x in enumerate(DATA[start:start+chunk]):
            rr=j//cols;cc=j%cols;xx=cc*cw;yy=rr*ch;ent=manifest.get(x['id'],{});fp=BASE/'out'/str(ent.get('file',''))
            if ent.get('file') and fp.exists():
                im=Image.open(fp).convert('RGB');im.thumbnail((180,112),Image.Resampling.LANCZOS);bx=xx+5+(180-im.width)//2;by=yy+3+(112-im.height)//2;sheet.paste(im,(bx,by))
            else:d.rectangle((xx+5,yy+3,xx+185,yy+115),outline=(120,120,120));d.text((xx+30,yy+48),'NO VERIFIED PHOTO',fill=(80,80,80),font=font)
            sc=ent.get('score','-');d.text((xx+5,yy+118),f"{x['id']} | {x['f']}",fill=(0,0,0),font=font);d.text((xx+5,yy+132),f"score {sc}",fill=(40,40,40),font=font)
        sheet.save(BASE/'out'/f'contact-{page:02d}.jpg','JPEG',quality=75,optimize=True)
except Exception as e:print('CONTACT_SHEET_ERR',e,flush=True)
print('DONE',len(manifest),'failures',len(failures),flush=True)
