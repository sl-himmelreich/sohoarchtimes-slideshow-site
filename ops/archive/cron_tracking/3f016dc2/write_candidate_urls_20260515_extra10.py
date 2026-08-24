import json
from urllib.parse import urlsplit, urlunsplit
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
out = base / 'candidate_urls_20260515_extra10.json'
published_path = base / 'published_objects.json'
daily_path = base / 'facts_20260515_daily5.json'

def norm(u: str) -> str:
    if not u:
        return ''
    p = urlsplit(u.strip())
    scheme = p.scheme.lower()
    netloc = p.netloc.lower().removeprefix('www.')
    path = p.path.rstrip('/')
    return urlunsplit((scheme, netloc, path, '', ''))

with open(published_path, encoding='utf-8') as f:
    published = json.load(f)
with open(daily_path, encoding='utf-8') as f:
    daily = json.load(f)
exclude = set()
for item in published + daily:
    for k in ('source_url','canonical_source_url'):
        if item.get(k):
            exclude.add(norm(item[k]))

candidates = [
  {
    "title": "O-14 / Reiser + Umemoto",
    "source_url": "https://www.archdaily.com/273404/o-14-reiser-umemoto",
    "source_name": "ArchDaily",
    "why_fit": "22-story commercial tower with a perforated concrete exoskeleton/diagrid: a systematic, variable envelope where openings respond to structural, opacity and environmental fields.",
    "built_evidence": "ArchDaily lists the project as completed/built, with Year 2010 and page evidence that it was completed in January 2011."
  },
  {
    "title": "Fondation Louis Vuitton / Gehry Partners",
    "source_url": "https://www.archdaily.com/555694/fondation-louis-vuitton-gehry-partners",
    "source_name": "ArchDaily",
    "why_fit": "Major cultural building driven by advanced digital design and fabrication: shared 3D model, robotic moulding and thousands of unique glass/concrete facade panels.",
    "built_evidence": "ArchDaily states the project was completed in 2014 in Paris and lists Year 2014."
  },
  {
    "title": "The Broad Museum / Diller Scofidio + Renfro",
    "source_url": "https://www.archdaily.com/772778/the-broad-diller-scofidio-plus-renfro",
    "source_name": "ArchDaily",
    "why_fit": "Advanced envelope case: the museum's porous honeycomb-like 'veil' spans the block-long building, filters daylight and wraps the sculptural storage vault.",
    "built_evidence": "ArchDaily describes The Broad as a completed 2015 museum in Los Angeles and lists Year 2015."
  },
  {
    "title": "King Fahad National Library / Gerber Architekten",
    "source_url": "https://www.archdaily.com/469088/king-fahad-national-library-gerber-architekten",
    "source_name": "ArchDaily",
    "why_fit": "Technological textile facade with rhomboid membrane awnings on a three-dimensional tensile steel-cable structure; sun path and light refraction optimization make it a strong advanced-envelope candidate.",
    "built_evidence": "ArchDaily states the library was completed and went into use in November 2013."
  },
  {
    "title": "Swatch and Omega Campus / Shigeru Ban Architects",
    "source_url": "https://www.archdaily.com/926166/swatch-and-omega-campus-shigeru-ban-architects",
    "source_name": "ArchDaily",
    "why_fit": "Hybrid mass-timber campus with a gridshell roof of 7,700 unique timber pieces designed by specialized software and fabricated to 0.1 mm precision.",
    "built_evidence": "ArchDaily lists the campus as completed in 2019 in Biel, Switzerland, with Year 2019."
  },
  {
    "title": "Hangzhou Olympic Sports Center / NBBJ",
    "source_url": "https://www.archdaily.com/940104/hangzhou-olympic-sports-center-nbbj",
    "source_name": "ArchDaily",
    "why_fit": "Large sports complex explicitly designed with parametric and computational scripts to reduce steel, optimize sightlines and integrate shell/bowl structural behavior.",
    "built_evidence": "ArchDaily lists the project as completed in 2019 in Hangzhou, China, with Year 2019."
  },
  {
    "title": "Ceramic House / Studio RAP",
    "source_url": "https://www.archdaily.com/1010548/ceramic-house-studio-rap",
    "source_name": "ArchDaily",
    "why_fit": "Built retail facade using algorithmic design, in-house digital design algorithms, robotic/digital fabrication and bespoke 3D-printed ceramic tiles.",
    "built_evidence": "ArchDaily lists Ceramic House as completed in 2023 in Amsterdam and gives Year 2023."
  },
  {
    "title": "The Henderson by Zaha Hadid Architects",
    "source_url": "https://www.archdaily.com/1031843/hong-kongs-queensway-reimagined-sara-klomps-on-the-genesis-and-ambition-of-the-henderson-by-zaha-hadid-architects",
    "source_name": "ArchDaily",
    "why_fit": "Completed tower with rationalized double-curved glass envelope, digitally controlled glass forming, operable high-performance facade and tightly coordinated building systems.",
    "built_evidence": "ArchDaily's interview states The Henderson was completed in April 2024 after design-to-construction from 2017."
  },
  {
    "title": "Sunac Guangzhou Grand Theatre by Steven Chilton Architects",
    "source_url": "https://parametric-architecture.com/sunac-guangzhou-grand-theatre-by-steven-chilton-architects/",
    "source_name": "Parametric Architecture",
    "why_fit": "Purpose-built theatre with a complex twisted red envelope; artist drawings were digitized and mapped onto geometry, then realized through thousands of perforated aluminium panels on welded steel frames.",
    "built_evidence": "Parametric Architecture describes it as a recently completed 2,000-seat purpose-built theatre that would open in 2021."
  },
  {
    "title": "Digital House blurs boundaries between design, fabrication, and construction with digital methods",
    "source_url": "https://parametric-architecture.com/digital-house-blurs-boundaries-between-design-fabrication-and-construction-with-digital-methods/",
    "source_name": "Parametric Architecture",
    "why_fit": "Small completed building entirely digitally designed/fabricated/assembled, with CNC-milled plywood, laser-cut parametrically designed aluminium facade sheets and plug-in construction details.",
    "built_evidence": "Parametric Architecture lists Project Year 2022 and Built / Unbuilt: Completed."
  },
  {
    "title": "Studio City – W Macau, designed by Zaha Hadid Architects, now open to the public",
    "source_url": "https://parametric-architecture.com/studio-city-w-macau-designed-by-zaha-hadid-architects-now-open-to-the-public/",
    "source_name": "Parametric Architecture",
    "why_fit": "Built hotel towers with high-performance insulated glazing, external shading fins and elliptical tower planning; a hospitality project in the ZHA computational/formal lineage, not a pavilion.",
    "built_evidence": "Parametric Architecture states ZHA finished W Macau at Studio City and that it is now open to the public."
  },
  {
    "title": "Busan Cinema Center has a unique ‘flying’ look due to its cantilever roof by Coop Himmelb(l)au",
    "source_url": "https://parametric-architecture.com/busan-cinema-center-has-a-unique-flying-look-due-to-its-cantilever-roof-by-coop-himmelblau/",
    "source_name": "Parametric Architecture",
    "why_fit": "Cultural complex with a world-record-scale 85 m cantilever roof, column-free canopy, articulated wavy ceiling and programmable LED media surface.",
    "built_evidence": "Parametric Architecture states construction began in late 2008 and ended four years later in 2012."
  },
  {
    "title": "Elbphilharmonie Hamburg / Herzog & de Meuron",
    "source_url": "https://www.archdaily.com/802093/elbphilharmonie-hamburg-herzog-and-de-meuron",
    "source_name": "ArchDaily",
    "why_fit": "Iconic cultural building with curved and carved-open glass facade panels, an undulating roof and complex hall geometry; strong advanced-envelope and computational-geometry fit.",
    "built_evidence": "ArchDaily lists Elbphilharmonie Hamburg as completed in 2016 in Hamburg and gives Year 2016."
  },
  {
    "title": "Mactan Cebu International Airport T2 / Integrated Design Associates",
    "source_url": "https://www.archdaily.com/942874/mactan-cebu-international-airport-t2-integrated-design-associates",
    "source_name": "ArchDaily",
    "why_fit": "Large transport building with modular glulam-arch roof arrays, integrated skylights/ducts and a lightweight typhoon/seismic strategy; a strong advanced structural envelope candidate.",
    "built_evidence": "ArchDaily lists the terminal as completed in 2018 in Cebu, Philippines, and gives Year 2018."
  },
  {
    "title": "Ordos Art & City Museum / MAD Architects",
    "source_url": "https://www.archdaily.com/211597/ordos-art-city-museum-mad-architects",
    "source_name": "ArchDaily",
    "why_fit": "Built amorphous museum wrapped in polished metal louvers with sinuous interior voids, bridges and canyon-like circulation; strong parametric/formal complexity fit beyond pavilion scale.",
    "built_evidence": "ArchDaily lists the museum as completed in 2011 in Ordos, China, with Year 2011."
  }
]

filtered = []
seen = set()
for c in candidates:
    n = norm(c['source_url'])
    if n in exclude:
        continue
    if n in seen:
        continue
    seen.add(n)
    filtered.append(c)

if len(filtered) < 12:
    raise SystemExit(f'Only {len(filtered)} candidates after filtering')
for c in filtered:
    n = norm(c['source_url'])
    if 'archdaily.com' not in n and 'parametric-architecture.com' not in n:
        raise SystemExit(f'Bad domain: {c["source_url"]}')
    if n in exclude:
        raise SystemExit(f'Excluded URL slipped through: {c["source_url"]}')
    if set(c) != {'title','source_url','source_name','why_fit','built_evidence'}:
        raise SystemExit(f'Bad fields: {c}')

out.write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {len(filtered)} candidates to {out}')
print('\n'.join(f"- {c['title']} | {c['source_url']}" for c in filtered))
