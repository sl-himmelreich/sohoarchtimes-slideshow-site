import json, sys, re, unicodedata, requests
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path('/home/user/workspace/cron_tracking/3f016dc2')
REGISTRY_NORM = ROOT / 'registry_normalized_20260401.json'
OUT = ROOT / 'image_validation_20260401.json'
TIMEOUT = 25
HEADERS = {'User-Agent': 'Mozilla/5.0'}

registry = json.loads(REGISTRY_NORM.read_text()) if REGISTRY_NORM.exists() else []
reg_urls = {x.get('source_url','') for x in registry} | {x.get('canonical_source_url','') for x in registry}
reg_titles = {x.get('title_norm','') for x in registry}

def norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace('&', ' and ')
    s = re.sub(r'https?://(www\.)?', '', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\b(architects?|architecture|tower|building|center|centre|museum|headquarters|office|offices|cultural|residential|station|the)\b', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def looks_duplicate(c):
    if c.get('source_url') in reg_urls or c.get('canonical_source_url') in reg_urls:
        return True, 'url already published'
    title_norm = norm(c.get('title',''))
    if title_norm in reg_titles:
        return True, 'title variant already published'
    return False, ''

def check_url(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        ct = (r.headers.get('content-type','') or '').lower()
        cl = int(r.headers.get('content-length','0') or 0)
        path = urlparse(url).path.lower()
        is_image_path = path.endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ok = r.status_code == 200 and cl > 50000 and ('image' in ct or is_image_path)
        return {'url': url, 'status': r.status_code, 'content_type': ct, 'content_length': cl, 'ok': ok}
    except Exception as e:
        return {'url': url, 'status': None, 'content_type': '', 'content_length': 0, 'ok': False, 'error': str(e)}

def main(path):
    candidates = json.loads(Path(path).read_text())
    out = []
    for c in candidates:
        dup, reason = looks_duplicate(c)
        checks = [check_url(u) for u in c.get('image_urls', [])]
        good = [x['url'] for x in checks if x.get('ok')]
        out.append({
            'title': c.get('title'),
            'source_url': c.get('source_url'),
            'duplicate': dup,
            'duplicate_reason': reason,
            'built_confirmed': c.get('built_confirmed'),
            'good_image_count': len(good),
            'good_image_urls': good[:5],
            'all_checks': checks,
            'candidate': c,
            'usable': (not dup) and c.get('built_confirmed') is True and len(good) >= 5
        })
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(str(OUT))

if __name__ == '__main__':
    main(sys.argv[1])