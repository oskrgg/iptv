"""Refresh my-cr.m3u: merge latest upstream links for each channel, re-add wanted
channels if upstream has them, test every link, keep only working ones.
usage: python3 -I refresh.py <my-cr.m3u> <upstream cr.m3u> <out.m3u>"""
import sys,re,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
WANTED=["Canal2","Canal6","Canal3KMKTV","Canal9","Canal17TVNosara","CartagoMediosTV","TigoSports"]
def parse(p):
    lines=open(p,encoding='utf-8').read().replace('\r','').splitlines(); out=[];buf=[]
    for l in lines[1:]:
        if not l.strip(): continue
        buf.append(l)
        if not l.startswith('#'): out.append(buf); buf=[]
    return out
cid=lambda e:(re.search(r'tvg-id="([^"]*)"',e[0]).group(1).split('@')[0])
name=lambda e:e[0].split(',',1)[1]
url=lambda e:e[-1]
mine=parse(sys.argv[1]); up=parse(sys.argv[2])
order=[]
for e in mine:
    if cid(e) not in order: order.append(cid(e))
for w in WANTED:
    if w+'.cr' not in order and any(cid(e)==w+'.cr' for e in up): order.append(w+'.cr')
cands=[]
for c in order:
    seen=set()
    for e in [e for e in up if cid(e)==c]+[e for e in mine if cid(e)==c]:
        if url(e) not in seen: seen.add(url(e)); cands.append(e)
import check
import concurrent.futures as cf
ex=cf.ThreadPoolExecutor(30)
futs=[ex.submit(check.check,name(e),url(e),next((l.split('=',1)[1] for l in e if l.startswith('#EXTVLCOPT:http-referrer=')),None)) for e in cands]
keep=[]
for e,f in zip(cands,futs):
    try: r=f.result(timeout=60)[2]
    except Exception: r="FAIL: timed out"
    if not r.startswith('OK'):  # retry twice: streams glitch briefly
        for _ in range(2):
            try: r=ex.submit(check.check,name(e),url(e),None).result(timeout=60)[2]
            except Exception: r="FAIL: timed out"
            if r.startswith('OK'): break
    print(f"{name(e)[:45]:45} {r}")
    if r.startswith('OK'): keep.append(e)
alpha=lambda e:[int(t) if t.isdigit() else t for t in re.split(r'(\d+)',name(e).split(' (')[0].lstrip('¡¿').lower())]
keep.sort(key=alpha)
# user wants only the resolution in names: drop [Geo-blocked], [Not 24/7] and any other [..] tag
untag=lambda l:re.sub(r'\s*\[[^\]]*\]','',l) if l.startswith('#EXTINF') else l
open(sys.argv[3],'w',encoding='utf-8').write("#EXTM3U\n"+"".join("\n".join(map(untag,e))+"\n" for e in keep))
print(f"\nkept {len(keep)} of {len(cands)} links; before: {len(mine)}")
sys.stdout.flush(); os._exit(0)
