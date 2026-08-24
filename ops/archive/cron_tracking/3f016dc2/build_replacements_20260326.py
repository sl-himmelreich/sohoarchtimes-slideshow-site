import json
from pathlib import Path

src = Path('/home/user/workspace/tool_calls/browser_task/output_mn731trs.json')
data = json.loads(src.read_text(encoding='utf-8'))['candidates']
by_title = {x['title']: x for x in data}
base = Path('/home/user/workspace/cron_tracking/3f016dc2/today_batch_20260326')

zigzag = by_title['Zigzag Tower / Atelier FCJZ']
softstone = by_title['SOFTSTONE Office Building / SETUParchitecture']

objs = [
    {
        'title': zigzag['title'],
        'slug': 'zigzag_tower_atelier_fcjz',
        'source_url': zigzag['source_url'],
        'canonical_source_url': zigzag['canonical_source_url'],
        'caption_ru': "Zigzag Tower\n\nЛокация: Чжэнчжоу, Китай\nАрхитектор: Atelier FCJZ\nГод реализации: 2016\nМатериалы: стеклянная фасадная система со складчатыми алюминиевыми ламелями, вынесенные наружу несущие колонны и безбалочная железобетонная конструктивная схема с центральными ядрами.\nКратко: офисная башня площадью около 39 000 м² превращает обычный прямоугольный объём в зигзагообразную высотную форму, отвечающую кривизне участка и раскрывающую больше угловых видов. Наружные колонны смещаются и сходятся по мере подъёма, делая структурную логику фасада главным пластическим мотивом здания и создавая выразительный вычислительно выверенный силуэт.",
        'image_urls': zigzag['image_urls'],
    },
    {
        'title': softstone['title'],
        'slug': 'softstone_office_building_setuparchitecture',
        'source_url': softstone['source_url'],
        'canonical_source_url': softstone['canonical_source_url'],
        'caption_ru': "SOFTSTONE Office Building\n\nЛокация: Тегеран, Иран\nАрхитектор: SETUParchitecture\nГод реализации: 2018\nМатериалы: предизготовленные каменные плиты переменного формата, смонтированные по параметрическому каркасу, и монолитная железобетонная основа, где геометрия оболочки учитывает допуски ручной резки камня и снижает отход материала.\nКратко: офисное здание трактует фасад не как набор отдельных плоскостей, а как непрерывную объёмную поверхность, которая стекает от кровли к улице и связывает уровни в единую пространственную систему. Проект особенно интересен тем, что вычислительная логика здесь работает не ради эффекта формы, а ради точной дискретизации каменной оболочки и более рациональной сборки на площадке.",
        'image_urls': softstone['image_urls'],
    }
]

for obj in objs:
    (base / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    print(obj['slug'])
