import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
outdir = base / 'today_batch_20260331'
outdir.mkdir(parents=True, exist_ok=True)
val = json.loads((base / 'image_validation_20260331.json').read_text(encoding='utf-8'))

objects = [
    {
        'title': 'One Thousand Museum Residential Tower / Zaha Hadid Architects',
        'slug': 'one_thousand_museum',
        'source_url': 'https://parametric-architecture.com/one-thousand-museum-residential-tower-erected-by-zaha-hadid-architects/',
        'canonical_source_url': 'https://parametric-architecture.com/one-thousand-museum-residential-tower-erected-by-zaha-hadid-architects/',
        'caption_ru': 'One Thousand Museum Residential Tower\n\nЛокация: Майами, США\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2020\nМатериалы: несущая concrete exoskeleton по периметру башни, permanent cladding из glass fibre reinforced concrete formwork, faceted façade с hurricane glazing на базе SentryGlas и Trosifol.\nКратко: One Thousand Museum стал одним из самых убедительных примеров того, как параметрическая логика может определять не только силуэт жилого небоскрёба, но и саму его конструктивную систему. Внешний экзоскелет одновременно работает как архитектурный образ, ветровая диагональная схема и способ освободить интерьеры от лишних колонн, превращая башню в цельную инженерно-пространственную оболочку.',
        'image_urls': val['one_thousand_museum']['ok_images'][:5],
    },
    {
        'title': 'RCC Headquarters / Foster + Partners',
        'slug': 'rcc_headquarters',
        'source_url': 'https://parametric-architecture.com/rcc-headquarters-features-triangulated-parts-inspired-by-the-crystal-lattice-of-copper/',
        'canonical_source_url': 'https://parametric-architecture.com/rcc-headquarters-features-triangulated-parts-inspired-by-the-crystal-lattice-of-copper/',
        'caption_ru': 'RCC Headquarters\n\nЛокация: Екатеринбург, Россия\nАрхитектор: Foster + Partners\nГод реализации: 2021\nМатериалы: энергоэффективная фасадная оболочка с triangulated элементами, геометрия которых вдохновлена crystal lattice of copper; двусветные модульные офисные ячейки выражены на фасаде как повторяющаяся пространственная сетка.\nКратко: штаб-квартира RCC интересна тем, что уходит от обычной схемы крупного корпоративного офиса и превращает фасад в прямое отражение внутренней организационной логики. Параметрическая треугольная система здесь не декоративна: она собирает идентичность бренда, модульность рабочих пространств и энергоэффективность в единый высотный образ.',
        'image_urls': val['rcc_headquarters']['ok_images'][:5],
    },
    {
        'title': 'Museum Tower Kyobashi / Nikken Sekkei',
        'slug': 'museum_tower_kyobashi',
        'source_url': 'https://www.archdaily.com/975692/the-museum-tower-kyobashi-nikken-sekkei',
        'canonical_source_url': 'https://www.archdaily.com/975692/the-museum-tower-kyobashi-nikken-sekkei',
        'caption_ru': 'Museum Tower Kyobashi\n\nЛокация: Токио, Япония\nАрхитектор: Nikken Sekkei\nГод реализации: 2019\nМатериалы: фасадная система из louvers, собранных из шести aluminum profiles одного сечения; комбинации рам меняются по сторонам башни и были оптимизированы через computational design analysis для контроля отражений и естественного света.\nКратко: башня Kyobashi соединяет музей и высококлассные офисы в одной тонко настроенной городской системе. Особенно важен здесь фасад, где вычислительный анализ используется не ради эффектной формы, а для точной настройки световой среды, визуального комфорта и масштаба высотного объёма в плотной исторической ткани центра Токио.',
        'image_urls': val['museum_tower_kyobashi']['ok_images'][:5],
    },
    {
        'title': "One Za'abeel Tower / Nikken Sekkei",
        'slug': 'one_zaabeel',
        'source_url': 'https://www.archdaily.com/1015281/one-zaabeel-tower-nikken-sekkei',
        'canonical_source_url': 'https://www.archdaily.com/1015281/one-zaabeel-tower-nikken-sekkei',
        'caption_ru': "One Za'abeel Tower\n\nЛокация: Дубай, ОАЭ\nАрхитектор: Nikken Sekkei\nГод реализации: 2023\nМатериалы: фасадная система с glass fins, задающими различное визуальное выражение башен и консольного объёма THE LINK; крупнопролётная связка THE LINK была смонтирована методом Incremental Launching Method.\nКратко: One Za'abeel важен как редкий реализованный мегапроект, где параметрическая координация формы, конструкции и монтажа читается в масштабе целого городского фрагмента. Две башни и гигантская консольная перемычка работают как единая пространственная машина, совмещая отель, офисы, жильё и общественные функции в одном сложном высотном комплексе.",
        'image_urls': val['one_zaabeel']['ok_images'][:5],
    },
    {
        'title': 'Stasys Museum / IMPLMNT architects',
        'slug': 'stasys_museum',
        'source_url': 'https://www.archdaily.com/1023136/stasys-museum-implmnt-architects',
        'canonical_source_url': 'https://www.archdaily.com/1023136/stasys-museum-implmnt-architects',
        'caption_ru': 'Stasys Museum\n\nЛокация: Паневежис, Литва\nАрхитектор: IMPLMNT architects\nГод реализации: 2023\nМатериалы: два типа текстурированного бетона с dotted и linear pattern, а также glazed facade system, подчинённая строгой пластике объёма.\nКратко: музей Stasys добавляет в сегодняшнюю пятёрку более сдержанный, но зрелый культурный объект, где выразительность строится не на перегруженной форме, а на точной работе с массой, разрезами и фактурой поверхности. Проект показывает, как современная цифровая дисциплина может проявляться через контроль геометрии, ритма и оболочки даже в лаконичной музейной архитектуре.',
        'image_urls': val['stasys_museum']['ok_images'][:5],
    },
]

for obj in objects:
    (outdir / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(outdir)
for obj in objects:
    print(obj['slug'])
