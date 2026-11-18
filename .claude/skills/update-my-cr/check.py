import sys,urllib.request,urllib.parse,ssl,concurrent.futures as cf
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA="Mozilla/5.0 (SMART-TV; Linux) VLC/3.0"
def get(u,ref,n=None):
    h={"User-Agent":UA}
    if ref: h["Referer"]=ref
    r=urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=10,context=ctx)
    return r.status, r.read(n or 300000)
def check(name,url,ref):
    try:
        s,b=get(url,ref); t=b.decode('utf-8','ignore')
        if len(b)>1000 and b[0]==0x47: return name,url,f"OK ({len(b)//1024} KB raw video received)"
        if '#EXTM3U' not in t: return name,url,f"FAIL: not a playlist (HTTP {s})"
        for _ in range(3):
            lines=[l.strip() for l in t.splitlines() if l.strip() and not l.startswith('#')]
            if not lines: return name,url,"FAIL: empty playlist"
            nxt=urllib.parse.urljoin(url,lines[0])
            if '#EXT-X-STREAM-INF' in t:
                s,b=get(nxt,ref); t=b.decode('utf-8','ignore'); url2=url; url=nxt; continue
            s,b=get(nxt,ref,200000)
            return name,url,f"OK ({len(b)//1024} KB video received)" if len(b)>1000 else f"FAIL: video chunk too small"
        return name,url,"FAIL: too many redirects"
    except urllib.error.HTTPError as e: return name,url,f"FAIL: HTTP {e.code}"
    except Exception as e: return name,url,f"FAIL: {type(e).__name__}: {str(e)[:60]}"
if __name__=='__main__':
    lines=[l.rstrip('\n') for l in open(sys.argv[1],encoding='utf-8')]
    entries=[];name=None;ref=None
    for l in lines[1:]:
        if l.startswith('#EXTINF'): name=l.split(',',1)[1]; ref=None
        elif l.startswith('#EXTVLCOPT:http-referrer='): ref=l.split('=',1)[1]
        elif l and not l.startswith('#'): entries.append((name,l,ref))
    ex=cf.ThreadPoolExecutor(30)
    futs=[ex.submit(check,*e) for e in entries]
    res=[]
    for f,e in zip(futs,entries):
        try: res.append(f.result(timeout=60))
        except Exception: res.append((e[0],e[1],"FAIL: timed out"))
    for i,(n,u,r) in enumerate(res,1): print(f"{i:2}. {n:45} {r}")
    
    import os; sys.stdout.flush(); os._exit(0)
