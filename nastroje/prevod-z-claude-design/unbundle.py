import sys, re, json, base64, gzip, os
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
def block(t):
    m = re.search(r'<script type="__bundler/%s">\s*(.*?)\s*</script>' % re.escape(t), html, re.S)
    return m.group(1) if m else None
manifest = json.loads(block('manifest'))
template = json.loads(block('template'))
ext = json.loads(block('ext_resources'))
os.makedirs(out, exist_ok=True)
print('assets:', len(manifest))
rows=[]
for uuid, e in manifest.items():
    raw = base64.b64decode(e['data'])
    data = gzip.decompress(raw) if e.get('compressed') else raw
    rows.append((uuid, e['mime'], len(e['data']), len(data), e.get('compressed')))
    ext_ = {'image/jpeg':'jpg','image/png':'png','image/webp':'webp','image/svg+xml':'svg','text/html':'html','text/css':'css','application/javascript':'js','text/javascript':'js','font/woff2':'woff2','image/gif':'gif','video/mp4':'mp4'}.get(e['mime'], 'bin')
    open(os.path.join(out, uuid+'.'+ext_),'wb').write(data)
open(os.path.join(out,'template.html'),'w',encoding='utf-8').write(template)
json.dump(ext, open(os.path.join(out,'ext.json'),'w'), indent=1)
rows.sort(key=lambda r:-r[3])
tot_b64=sum(r[2] for r in rows); tot=sum(r[3] for r in rows)
print('total b64 in file: %.2f MB, decoded: %.2f MB'%(tot_b64/1e6, tot/1e6))
for r in rows: print('%s %-22s b64=%9d decoded=%9d gz=%s'%r)
print('template length', len(template))
