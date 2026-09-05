import json, urllib.request, urllib.parse, time, gzip, io, sys
BASE="https://api.openalex.org/works"
params={"filter":"is_retracted:true","per-page":"200",
        "select":"doi,publication_year,cited_by_count,counts_by_year,type",
        "mailto":"tnriley@gmail.com"}
cursor="*"; out=[]; t0=time.time(); pages=0; total=None
while cursor:
    p=dict(params); p["cursor"]=cursor
    url=BASE+"?"+urllib.parse.urlencode(p)
    for attempt in range(4):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"daybook-nightly/1.0 (mailto:tnriley@gmail.com)","Accept-Encoding":"gzip"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw=r.read()
                if r.headers.get("Content-Encoding")=="gzip": raw=gzip.decompress(raw)
            d=json.loads(raw); break
        except Exception as e:
            if attempt==3: raise
            time.sleep(2*(attempt+1))
    if total is None:
        total=d["meta"]["count"]; print("total works:", total, flush=True)
    out.extend(d["results"]); pages+=1
    cursor=d["meta"].get("next_cursor")
    if pages%50==0:
        print(f"  {len(out):>7}/{total}  {time.time()-t0:5.0f}s", flush=True)
    if not d["results"]: break
json.dump(out, open("openalex_retracted.json","w"))
print(f"DONE {len(out)} records in {time.time()-t0:.0f}s", flush=True)
