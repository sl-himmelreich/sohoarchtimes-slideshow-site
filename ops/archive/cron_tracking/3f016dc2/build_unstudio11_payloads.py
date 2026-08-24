#!/usr/bin/env python3
import json
import re
from pathlib import Path

facts_path = Path('/home/user/workspace/cron_tracking/3f016dc2/facts_20260512_unstudio11_raw.json')
captions_path = Path('/home/user/workspace/cron_tracking/3f016dc2/captions_20260512_unstudio11_opus.json')
out_dir = Path('/home/user/workspace/cron_tracking/3f016dc2/today_batch_20260512_unstudio11')
out_dir.mkdir(parents=True, exist_ok=True)

facts = json.loads(facts_path.read_text(encoding='utf-8'))
captions_data = json.loads(captions_path.read_text(encoding='utf-8'))

caption_map = {}
if isinstance(captions_data, list):
    for item in captions_data:
        if isinstance(item, dict) and item.get('title') and (item.get('caption_ru') or item.get('caption')):
            caption_map[item['title'].strip()] = (item.get('caption_ru') or item.get('caption')).strip()
elif isinstance(captions_data, dict):
    if isinstance(captions_data.get('captions'), list):
        for item in captions_data['captions']:
            if isinstance(item, dict) and item.get('title') and (item.get('caption_ru') or item.get('caption')):
                caption_map[item['title'].strip()] = (item.get('caption_ru') or item.get('caption')).strip()
    else:
        for k, v in captions_data.items():
            if isinstance(v, str):
                caption_map[k.strip()] = v.strip()
            elif isinstance(v, dict) and (v.get('caption_ru') or v.get('caption')):
                caption_map[k.strip()] = (v.get('caption_ru') or v.get('caption')).strip()

missing = []
for item in facts:
    title = item['title'].strip()
    caption = caption_map.get(title)
    if not caption:
        missing.append(title)
        continue
    payload = {
        'title': item['title'],
        'slug': item['slug'],
        'source_url': item['source_url'],
        'canonical_source_url': item.get('canonical_source_url', ''),
        'caption_ru': caption,
        'image_urls': item['image_urls']
    }
    if item.get('allow_duplicate'):
        payload['allow_duplicate'] = True
        if item.get('duplicate_reason'):
            payload['duplicate_reason'] = item['duplicate_reason']
    out_path = out_dir / f"{item['slug']}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

print(json.dumps({'out_dir': str(out_dir), 'missing': missing, 'count': len(list(out_dir.glob('*.json')))}, ensure_ascii=False))
