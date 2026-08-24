import json
from pathlib import Path

ROOT = Path('/home/user/workspace/cron_tracking/3f016dc2')
VAL_PATH = ROOT / 'image_validation_20260401.json'
OUTDIR = ROOT / 'today_batch_20260401'
OUTDIR.mkdir(exist_ok=True)

validation = json.loads(VAL_PATH.read_text(encoding='utf-8'))
by_title = {row['title']: row for row in validation if row.get('usable')}

posts = [
    {
        'title': 'Metropolitan Railway Station features mushroom pillars made of latticed steel',
        'title_out': 'Metropolitan Railway Station',
        'slug': 'metropolitan-railway-station-lublin',
        'caption_ru': 'Metropolitan Railway Station\nЛокация: Люблин, Польша\nАрхитектор: Tremend Architecture Studio\nГод реализации: 2023\nМатериалы: решётчатые грибовидные опоры и навес из нержавеющей стали, стеклянное заполнение покрытия, энергоэффективная LED-подсветка, система сбора дождевой воды для полива и озеленения.\nКлючевой элемент транспортного хаба Люблина — станция с выразительным навесом, где тонкие стальные опоры работают одновременно как несущая система и как городской образ. Параметрическая геометрия покрытия собирает платформенное пространство в единый общественный зал и обновляет окружающий вокзальный район.'
    },
    {
        'title': 'Songjiang Art Campus / Archi-Union Architects',
        'title_out': 'Songjiang Art Campus',
        'slug': 'songjiang-art-campus-shanghai',
        'caption_ru': 'Songjiang Art Campus\nЛокация: Шанхай, Китай\nАрхитектор: Archi-Union Architects\nГод реализации: 2015\nКрупный культурно-образовательный комплекс площадью 150 000 м² построен как система цифрово спроектированных модулей, общественных проходов и озеленённых связей. Криволинейные и ломаные объёмы формируют плотную, но читаемую среду, где архитектура кампуса работает как последовательность городских пространств для искусства, обучения и повседневной активности.'
    },
    {
        'title': "Zaha Hadid's Port House: A Floating Crystal Crown Above the City",
        'title_out': 'Port House',
        'slug': 'port-house-antwerp',
        'caption_ru': 'Port House\nЛокация: Антверпен, Бельгия\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2016\nМатериалы: пространственная стальная ферма, ограждающая оболочка из гранёных стеклянных панелей, две скульптурные бетонные опоры, несущие кристаллический объём над историческим пожарным депо.\nШтаб-квартира порта Антверпена соединяет реконструкцию существующего здания с вынесенным в консоль новым объёмом, напоминающим огранённый алмаз и нос корабля одновременно. Проект собирает администрацию под одной крышей и превращает индустриальный контекст гавани в яркий символ цифрово рассчитанной конструктивной пластики.'
    },
    {
        'title': 'Lightrailstation The Hague / architectural studio ZJA',
        'title_out': 'Lightrailstation The Hague',
        'slug': 'lightrailstation-the-hague',
        'caption_ru': 'Lightrailstation The Hague\nЛокация: Гаага, Нидерланды\nАрхитектор: architectural studio ZJA\nГод реализации: 2016\nМатериалы: пространственная кровля из стальных элементов и стеклянного заполнения, геометрия покрытия оптимизирована параметрическими и вычислительными инструментами.\nСтанция легкорельсового транспорта решена как единый текучий навес, связанный с соседним виадуком и городской инфраструктурой. Лёгкая оболочка защищает платформы от ветра и дождя, пропускает дневной свет и превращает вход в транспортный узел в выразительный городской ориентир.'
    },
    {
        'title': "Zaha Hadid Architects' First Built Tower: CMA CGM Headquarters",
        'title_out': 'CMA CGM Headquarters',
        'slug': 'cma-cgm-headquarters-marseille',
        'caption_ru': 'CMA CGM Headquarters\nЛокация: Марсель, Франция\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2010\nПервая реализованная высотная башня Zaha Hadid Architects собрана из изогнутых объёмов, которые сходятся и расходятся по мере роста здания, формируя характерный вертикальный силуэт на набережной Марселя. Пластика башни переводит параметры движения, перспективы и нагрузки в цельный образ штаб-квартиры глобальной морской компании.'
    }
]

written = []
for post in posts:
    row = by_title[post['title']]
    candidate = row['candidate']
    obj = {
        'title': post['title_out'],
        'slug': post['slug'],
        'source_url': candidate['source_url'],
        'canonical_source_url': candidate.get('canonical_source_url', ''),
        'caption_ru': post['caption_ru'],
        'image_urls': row['good_image_urls'][:5]
    }
    path = OUTDIR / f"{post['slug']}.json"
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    written.append(str(path))

print('\n'.join(written))
