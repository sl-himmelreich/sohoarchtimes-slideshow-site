import json, re, requests, sys
from pathlib import Path

pages = {
    'rcc_hq': 'https://parametric-architecture.com/rcc-headquarters-features-triangulated-parts-inspired-by-the-crystal-lattice-of-copper/',
    'shenzhen_museum': 'https://parametric-architecture.com/zaha-hadid-architects-shenzhen-science-and-technology-museum/',
    'jomoo_hq': 'https://parametric-architecture.com/oma-jomoo-headquarters-china/',
    'origami_office': 'https://parametric-architecture.com/manuelle-gautrand-designs-an-office-building-with-a-folded-glass-facade-resembling-japanese-origami/',
    'termeh': 'https://parametric-architecture.com/termeh-office-commercial-building-has-a-wave-like-design-that-blends-with-its-surroundings/',
    'communique': 'https://www.archdaily.com/780596/communique-headquarters-daewha-kang-design',
}

headers = {'User-Agent': 'Mozilla/5.0'}
out = {}
for slug, url in pages.items():
    try:
        html = requests.get(url, headers=headers, timeout=60).text
    except Exception as e:
        out[slug] = {'url': url, 'error': str(e)}
        continue
    if 'archdaily.com' in url:
        imgs = re.findall(r'https://images\.adsttc\.com/[^"\'\s>]+large_jpg/[^"\'\s>]+', html)
    else:
        imgs = re.findall(r'https://parametric-architecture\.com/wp-content/uploads/[^"\'\s>]+', html)
    # de-dupe preserve order
    seen = set(); dedup=[]
    for x in imgs:
        x = x.replace('\\/', '/')
        if x not in seen:
            seen.add(x); dedup.append(x)
    out[slug] = {'url': url, 'image_count': len(dedup), 'images': dedup[:20]}

out_path = Path('/home/user/workspace/cron_tracking/3f016dc2/today_candidate_image_scan_20260327.json')
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(out_path)
for k,v in out.items():
    print(k, v.get('image_count'), v.get('error',''))
