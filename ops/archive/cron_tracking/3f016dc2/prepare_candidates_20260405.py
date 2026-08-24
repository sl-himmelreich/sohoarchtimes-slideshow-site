import json, re, unicodedata
from pathlib import Path

ROOT = Path('/home/user/workspace/cron_tracking/3f016dc2')
REGISTRY = ROOT / 'published_objects.json'
OUT = ROOT / 'registry_normalized_20260405.json'

def norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace('&', ' and ')
    s = re.sub(r'https?://(www\.)?', '', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\b(architects?|architecture|tower|building|center|centre|museum|headquarters|office|offices|cultural|residential|station|the|new|venue|project)\b', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
rows = []
for item in registry:
    rows.append({
        'title': item.get('title',''),
        'title_norm': norm(item.get('title','')),
        'source_url': item.get('source_url',''),
        'canonical_source_url': item.get('canonical_source_url',''),
        'telegram_message_id': item.get('telegram_message_id')
    })
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(str(OUT))