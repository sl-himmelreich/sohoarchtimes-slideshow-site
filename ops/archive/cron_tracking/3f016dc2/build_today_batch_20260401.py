import json, re
from pathlib import Path

ROOT = Path('/home/user/workspace/cron_tracking/3f016dc2')
VAL = ROOT / 'image_validation_20260401.json'
OUTDIR = ROOT / 'today_batch_20260401'
OUTDIR.mkdir(exist_ok=True)

SELECT_TITLES = [
    'Metropolitan Railway Station features mushroom pillars made of latticed steel',
    'Songjiang Art Campus / Archi-Union Architects',
    'PORT_HOUSE_PLACEHOLDER',
    'CANTON_TOWER_PLACEHOLDER',
    'MAHANAKHON_PLACEHOLDER'
]

TITLE_OVERRIDES_RU = {
    'Metropolitan Railway Station features mushroom pillars made of latticed steel': 'Metropolitan Railway Station',
    'Songjiang Art Campus / Archi-Union Architects': 'Songjiang Art Campus',
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]

def caption_ru(c):
    title = TITLE_OVERRIDES_RU.get(c['title'], c['title'].split(' / ')[0].replace("Zaha Hadid Architects' First Built Tower: ", '').strip())
    lines = [title]
    if c.get('location'):
        lines.append(f"Локация: {c['location']}")
    if c.get('architects'):
        lines.append(f"Архитектор: {c['architects']}")
    if c.get('year'):
        lines.append(f"Год реализации: {c['year']}")
    if c.get('materials_detail'):
        md = c['materials_detail'].strip().rstrip('.')
        if md and md.lower() not in {'concrete, brick', 'glass, steel', 'glass and steel roof/canopy structure; parametric and computational design methods used for spatial roof optimization', 'glass and steel'}:
            lines.append(f"Материалы: {md}")
    summary = c.get('summary_ru') or c.get('summary_en','').strip().rstrip('.')
    if summary:
        lines.append(summary)
    return '\n'.join(lines)

val = json.loads(VAL.read_text())
usable = {row['title']: row for row in val if row.get('usable')}
written = []
for title in SELECT_TITLES:
    if title not in usable:
        continue
    c = usable[title]['candidate']
    obj = {
        'title': c['title'],
        'slug': slugify(c['title']),
        'source_url': c['source_url'],
        'canonical_source_url': c.get('canonical_source_url',''),
        'caption_ru': caption_ru(c),
        'image_urls': usable[title]['good_image_urls'][:5]
    }
    out = OUTDIR / f"{obj['slug']}.json"
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    written.append(str(out))
print('\n'.join(written))
