import json, re, requests, time
from pathlib import Path

BASE = Path('/home/user/workspace/cron_tracking/3f016dc2')
OUT = BASE / 'image_validation_20260329.json'
HTML_DIR = BASE / 'html_20260329'
HTML_DIR.mkdir(parents=True, exist_ok=True)

pages = {
    'dfab_house': 'https://www.archdaily.com/942221/dfab-house-eth-zurich-plus-nccr-digital-fabrication',
    'maslak_no1': 'https://www.archdaily.com/800160/maslak-n-office-tower-emre-arolat-architects',
    'malta_maritime_trade_centre': 'https://www.archdaily.com/502293/malta-maritime-trade-centre-architecture-project',
    'thirty_st_mary_axe': 'https://www.archdaily.com/928285/30-st-mary-axe-tower-foster-plus-partners',
    'da_nang_hitech_hq': 'https://www.archdaily.com/1027308/da-nang-hi-tech-park-headquarters-building-huni-architectes',
    'hospital_manta': 'https://www.archdaily.com/928430/hospital-manta-pmmt',
}

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'en-US,en;q=0.9',
}
img_headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
}
pattern = re.compile(r'https://images\.adsttc\.com/[^"\'\s>]+(?:medium|large)_jpg/[^"\'\s>]+')
results = {}

for slug, url in pages.items():
    try:
        r = session.get(url, headers=headers, timeout=90)
        r.raise_for_status()
        html = r.text
        (HTML_DIR / f'{slug}.html').write_text(html, encoding='utf-8')
        raw = pattern.findall(html)
        candidates = []
        seen = set()
        for u in raw:
            u = u.replace('\\/', '/')
            u = u.replace('/medium_jpg/', '/large_jpg/')
            if u not in seen:
                seen.add(u)
                candidates.append(u)
        checked = []
        ok = []
        for img in candidates:
            good = False
            status = None
            ctype = ''
            size = 0
            for attempt in range(2):
                try:
                    rr = session.get(img, headers={**img_headers, 'Referer': url}, timeout=90, stream=True, allow_redirects=True)
                    status = rr.status_code
                    ctype = rr.headers.get('content-type', '')
                    content = rr.raw.read(65536, decode_content=False)
                    size = int(rr.headers.get('content-length', '0') or 0)
                    good = status == 200 and ctype.startswith('image/') and (size > 50000 or len(content) > 20000)
                    rr.close()
                    if good:
                        ok.append(img)
                        break
                except Exception:
                    pass
                time.sleep(attempt + 1)
            checked.append({'url': img, 'status': status, 'ctype': ctype, 'size': size, 'good': good})
            if len(ok) >= 7:
                break
        results[slug] = {
            'source_url': url,
            'raw_count': len(raw),
            'candidate_count': len(candidates),
            'ok_count': len(ok),
            'ok_images': ok[:7],
            'checked': checked,
        }
    except Exception as e:
        results[slug] = {'source_url': url, 'error': str(e)}

OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(str(OUT))
for slug, data in results.items():
    print(slug, data.get('ok_count'), data.get('error', ''))
