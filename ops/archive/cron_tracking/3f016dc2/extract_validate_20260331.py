import json
from pathlib import Path
import requests

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
candidates = json.loads((base / 'candidates_20260331.json').read_text(encoding='utf-8'))
out = {}
s = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0'}

for cand in candidates:
    checked = []
    ok = []
    for url in cand['images']:
        try:
            r = s.get(url, headers=headers, timeout=45, allow_redirects=True, stream=True)
            content = r.raw.read(65536, decode_content=True)
            ctype = r.headers.get('content-type', '')
            size = int(r.headers.get('content-length', '0') or '0')
            if size == 0:
                size = len(content)
            good = r.status_code == 200 and ctype.startswith('image/') and size > 50000
            checked.append({'url': url, 'status': r.status_code, 'ctype': ctype, 'size': size, 'good': good})
            if good:
                ok.append(url)
            if len(ok) >= 7:
                break
        except Exception as e:
            checked.append({'url': url, 'status': 'ERR', 'ctype': '', 'size': 0, 'good': False, 'error': str(e)})
    out[cand['slug']] = {
        'title': cand['title'],
        'source_url': cand['source_url'],
        'ok_count': len(ok),
        'ok_images': ok,
        'checked': checked,
    }

(base / 'image_validation_20260331.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(base / 'image_validation_20260331.json')
for k,v in out.items():
    print(k, v['ok_count'])
