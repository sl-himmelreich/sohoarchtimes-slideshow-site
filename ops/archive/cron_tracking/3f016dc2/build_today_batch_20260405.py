import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
final_candidates = json.loads((base / 'final_candidates_20260405.json').read_text(encoding='utf-8'))
validation = json.loads((base / 'image_validation_20260405.json').read_text(encoding='utf-8'))
out_dir = base / 'today_batch_20260405'
out_dir.mkdir(parents=True, exist_ok=True)

val_map = {item['source_url']: item for item in validation if item.get('usable')}
cand_map = {item['source_url']: item for item in final_candidates}

selected = [
    'https://www.archdaily.com/1006370/new-venue-of-the-yuz-museum-scenic-architecture-office',
    'https://www.archdaily.com/1013811/anrenfang-heritage-museum-and-anren-station-ddb-architects',
    'https://www.archdaily.com/1024201/king-abdullah-financial-district-metro-station-zaha-hadid-architects',
    'https://www.archdaily.com/783216/shanghai-tower-gensler',
    'https://www.archdaily.com/902285/venue-b-of-shanghai-westbund-world-artificial-intelligence-conference-archi-union-architecture',
]

payloads = {
    'https://www.archdaily.com/1006370/new-venue-of-the-yuz-museum-scenic-architecture-office': {
        'title': 'New Venue of the Yuz Museum / Scenic Architecture Office',
        'slug': 'new-venue-of-the-yuz-museum-shanghai',
        'caption_ru': 'New Venue of the Yuz Museum\nЛокация: Панлун, район Чунмин, Шанхай, Китай\nАрхитектор: Scenic Architecture Office\nГод реализации: 2023\nМатериалы: пространственный стальной каркас, стеклянные ограждения, бетонные элементы, формирующие наружные галереи, дворовые пространства и переходные зоны, переосмысляющие типологию традиционных домов региона Цзяннань.\nНовая площадка музея Yuz устроена как последовательность дворов, коридоров и открытых выставочных маршрутов между ландшафтом водно-болотной территории и городской кромкой. Проект делает культурный объект почти ландшафтным, а его архитектуру строит на многослойных порогах, полузакрытых пространствах и мягком переходе между интерьером и внешней средой.'
    },
    'https://www.archdaily.com/1013811/anrenfang-heritage-museum-and-anren-station-ddb-architects': {
        'title': 'Anrenfang Heritage Museum and Anren Station / DDB Architects',
        'slug': 'anrenfang-heritage-museum-and-anren-station-xian',
        'caption_ru': 'Anrenfang Heritage Museum and Anren Station\nЛокация: Сиань, Шэньси, Китай\nАрхитектор: DDB Architects\nГод реализации: 2022\nМатериалы: стеклянное покрытие с системой Beam String Structure над археологическим залом, облицовка из titanium-zinc панелей, массивные деревянные решётки, стеклянные curtain walls и матовая металлическая кровля, собирающая современный образ традиционной черепичной линии.\nКомплекс совмещает музей археологических находок и транспортный узел у исторической зоны Малой пагоды диких гусей. Архитектура переводит логику танской городской сетки и дворовой структуры в современный общественный объект, где инфраструктура, археология и музейный сценарий работают как единое пространственное целое.'
    },
    'https://www.archdaily.com/1024201/king-abdullah-financial-district-metro-station-zaha-hadid-architects': {
        'title': 'King Abdullah Financial District Metro Station / Zaha Hadid Architects',
        'slug': 'king-abdullah-financial-district-metro-station-riyadh',
        'caption_ru': 'King Abdullah Financial District Metro Station\nЛокация: Эр-Рияд, Саудовская Аравия\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2024\nМатериалы: самонесущая пространственная оболочка и конструкция станции, собранные как трёхмерная стальная решётка из повторяющихся криволинейных арок; геометрия оптимизирована под структурную эффективность и экологическую производительность.\nСтанция стала одним из самых выразительных узлов метро Эр-Рияда. Её волнообразная оболочка объединяет навес, фасад и внутренние залы в непрерывную транспортную архитектуру, где параметрическая геометрия напрямую работает на поток пассажиров, климатическую защиту и конструктивную логику.'
    },
    'https://www.archdaily.com/783216/shanghai-tower-gensler': {
        'title': 'Shanghai Tower / Gensler',
        'slug': 'shanghai-tower-shanghai',
        'caption_ru': 'Shanghai Tower\nЛокация: Пудун, Шанхай, Китай\nАрхитектор: Gensler; Architect of Record: Architectural Design & Research Institute of Tongji University (Group) Co., Ltd.\nГод реализации: 2015\nМатериалы: двойная стеклянная фасадная оболочка с применением Kuraray SentryGlas и Trosifol architectural glazing во внешнем слое, стальной мегакаркас и железобетонное ядро.\nСверхвысокая башня высотой 632 метра формирует спиральный объём с поворотом по мере роста, чтобы снижать ветровые нагрузки и создавать систему вертикальных общественных атриумов. Это один из ключевых примеров того, как вычислительное формообразование, инженерная оптимизация и экологическая стратегия сходятся в масштабе настоящего городского мегаструктурного объекта.'
    },
    'https://www.archdaily.com/902285/venue-b-of-shanghai-westbund-world-artificial-intelligence-conference-archi-union-architecture': {
        'title': 'Venue B of Shanghai Westbund World Artificial Intelligence Conference / Archi-Union Architecture',
        'slug': 'venue-b-shanghai-westbund-waic-shanghai',
        'caption_ru': 'Venue B of Shanghai Westbund World Artificial Intelligence Conference\nЛокация: Шанхай, Китай\nАрхитектор: Archi-Union Architecture\nГод реализации: 2018\nМатериалы: параметрическая деревянная оболочка, лёгкая prefabricated aluminum truss system, роботически напечатанный полупрозрачный полимерный павильон и filament pavilion из fiber-composite элементов, дополненные стеклом, сталью и мембранными покрытиями.\nКомплекс для конференции по искусственному интеллекту задуман как демонстратор архитектуры вычислительного проектирования и цифрового производства в полном масштабе. Связанные между собой залы, деревянная параметрическая кровля и экспериментальные цифрово изготовленные структуры превращают выставочную площадку в каталог актуальных методов robotic fabrication и material-driven design.'
    },
}

written = []
for url in selected:
    cand = cand_map[url]
    val = val_map[url]
    payload = {
        'title': payloads[url]['title'],
        'slug': payloads[url]['slug'],
        'source_url': cand['source_url'],
        'canonical_source_url': cand.get('canonical_source_url', cand['source_url']),
        'caption_ru': payloads[url]['caption_ru'],
        'image_urls': val['good_image_urls'][:5],
    }
    path = out_dir / f"{payload['slug']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    written.append(str(path))

print(json.dumps({'written': written}, ensure_ascii=False, indent=2))
