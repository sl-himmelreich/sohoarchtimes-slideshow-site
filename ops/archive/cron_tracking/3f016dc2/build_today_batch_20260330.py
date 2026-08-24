import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
outdir = base / 'today_batch_20260330'
outdir.mkdir(parents=True, exist_ok=True)
val = json.loads((base / 'image_validation_20260330.json').read_text(encoding='utf-8'))

objects = [
    {
        'title': 'Morpheus Hotel / Zaha Hadid Architects',
        'slug': 'morpheus_hotel',
        'source_url': 'https://www.archdaily.com/896433/morpheus-hotel-zaha-hadid-architects',
        'canonical_source_url': 'https://www.archdaily.com/896433/morpheus-hotel-zaha-hadid-architects',
        'caption_ru': 'Morpheus Hotel\n\nЛокация: Котай, Макао\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2018\nМатериалы: пространственная free-form high-rise exoskeleton с переменной плотностью диагридной сетки, где массивные нижние structural members постепенно переходят к более лёгкой верхней структуре, формируя несущую внешнюю оболочку без внутренних колонн в ключевых общественных пространствах.\nКратко: Morpheus показывает, как вычислительная геометрия может работать в масштабе полноценной высотной гостиницы, а не только в формате экспериментального павильона. Башня вырезана тремя крупными пустотами, которые превращают центральную часть объёма в серию связных атриумов и городских окон, а внешняя несущая оболочка одновременно решает задачи образа, конструкции и свободной внутренней планировки.',
        'image_urls': val['morpheus_hotel']['ok_images'][:5],
    },
    {
        'title': 'Lumina Shanghai / Gensler',
        'slug': 'lumina_shanghai',
        'source_url': 'https://www.archdaily.com/989776/lumina-shanghai-gensler',
        'canonical_source_url': 'https://www.archdaily.com/989776/lumina-shanghai-gensler',
        'caption_ru': 'Lumina Shanghai\n\nЛокация: Шанхай, Китай\nАрхитектор: Gensler\nГод реализации: 2022\nМатериалы: Low-E IGU façade system, трёхмерные textured vertical decorative fins для солнцезащиты, прозрачная стеклянная оболочка с повышенным доступом естественного света; 34% применённых материалов указаны как reusable или recycled.\nКратко: 280-метровая башня на West Bund интересна тем, что параметрическая логика здесь встроена в коммерческий небоскрёб высокого класса и работает через климатическую оболочку, а не через чистый жест формы. Вертикальные рёбра, глубина фасада и светопропускание собраны в единую систему, которая усиливает силуэт здания на набережной и одновременно снижает солнечную нагрузку и повышает энергетическую эффективность.',
        'image_urls': val['lumina_shanghai']['ok_images'][:5],
    },
    {
        'title': 'Malta Maritime Trade Centre / AP Valletta',
        'slug': 'malta_maritime_trade_centre',
        'source_url': 'https://www.archdaily.com/502293/malta-maritime-trade-centre-architecture-project',
        'canonical_source_url': 'https://www.archdaily.com/502293/malta-maritime-trade-centre-architecture-project',
        'caption_ru': 'Malta Maritime Trade Centre\n\nЛокация: Марса, Мальта\nАрхитектор: AP Valletta\nГод реализации: 2007\nМатериалы: наружные metal louvered screens из anodized aluminium, собранные из цилиндрических элементов диаметром 30 мм с вертикальным шагом 100 мм, вертикальным framing с шагом 1 м и горизонтальными обслуживающими walkway в 650-миллиметровом зазоре между экраном и основной фасадной плоскостью.\nКратко: этот офисный комплекс важен как ранний пример того, как параметрическое исследование приводит не к абстрактной форме, а к точной рабочей фасадной системе. Алюминиевый экран был рассчитан так, чтобы одновременно сохранять виды на гавань, уменьшать перегрев южных фасадов и снижать нагрузку на охлаждение, превращая оболочку здания в настроенный экологический инструмент.',
        'image_urls': val['malta_maritime_trade_centre']['ok_images'][:5],
    },
    {
        'title': 'Ali Mohammed T. Al-Ghanim Clinic / AGi architects',
        'slug': 'ali_al_ghanim_clinic',
        'source_url': 'https://www.archdaily.com/611323/ali-mohammed-t-al-ghanim-clinic-agi-architects',
        'canonical_source_url': 'https://www.archdaily.com/611323/ali-mohammed-t-al-ghanim-clinic-agi-architects',
        'caption_ru': 'Ali Mohammed T. Al-Ghanim Clinic\n\nЛокация: Кувейт\nАрхитектор: AGi Architects\nГод реализации: 2014\nМатериалы: внешняя вуаль из anodized and perforated metal sheet, цветовые акценты и система навигации из colorful ceramic mosaic, интегрированные в дворовую и фасадную композицию медицинского центра.\nКратко: клиника интересна тем, что переводит приёмы параметрического и климатически чувствительного проектирования в типологию здравоохранения. Внутренние дворы вырезаны из объёма так, чтобы обеспечить приватность, естественный свет, вентиляцию и мягкую пространственную ориентацию, а перфорированная металлическая оболочка создаёт фильтр между городом и медицинской программой.',
        'image_urls': val['ali_al_ghanim_clinic']['ok_images'][:5],
    },
    {
        'title': 'LanQiao Clubhouse / HHD_FUN Architects',
        'slug': 'lanqiao_clubhouse',
        'source_url': 'https://www.archdaily.com/290317/lanqiao-clubhouse-hhd_fun-architects',
        'canonical_source_url': 'https://www.archdaily.com/290317/lanqiao-clubhouse-hhd_fun-architects',
        'caption_ru': 'LanQiao Clubhouse\n\nЛокация: пляжный парк Shanhaitian, Жичжао, Китай\nАрхитектор: HHD_FUN Architects\nКратко: клубный павильон на побережье ценен не размером, а тем, как параметрическая модель была адаптирована к локальному производству и строительным ограничениям. Сложная криволинейная форма, большой пролёт без промежуточных опор и минимальное вмешательство в существующий сосновый массив собраны здесь в объект, который показывает практику low-technology parametric design как реальную строительную тактику, а не только цифровой эксперимент.',
        'image_urls': val['lanqiao_clubhouse']['ok_images'][:5],
    },
]

for obj in objects:
    (outdir / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(outdir)
for obj in objects:
    print(obj['slug'])
