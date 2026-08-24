import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
outdir = base / 'today_batch_20260329'
outdir.mkdir(parents=True, exist_ok=True)
val = json.loads((base / 'image_validation_20260329.json').read_text(encoding='utf-8'))

objects = [
    {
        'title': 'DFAB House / NCCR Digital Fabrication',
        'slug': 'dfab_house',
        'source_url': 'https://www.archdaily.com/942221/dfab-house-eth-zurich-plus-nccr-digital-fabrication',
        'canonical_source_url': 'https://www.archdaily.com/942221/dfab-house-eth-zurich-plus-nccr-digital-fabrication',
        'caption_ru': 'DFAB House\n\nЛокация: Дюбендорф, Швейцария\nАрхитектор: NCCR Digital Fabrication\nГод реализации: 2019\nМатериалы: Lightweight Translucent Facade на основе мембранной оболочки с translucent thermal insulation из Aerogel, Mesh Mould — роботизированная безопалубочная система для steel-reinforced concrete, Smart Dynamic Casting для автоматизированного slip-forming бетона, Smart Slab с 3D-printed formwork, Spatial Timber Assemblies и индивидуально изготовленные curved concrete mullions.\nКратко: DFAB House стал одним из первых полноразмерных жилых объектов, где цифровое проектирование и роботизированное производство формируют не отдельные детали, а весь строительный процесс как связанную систему. Особая ценность проекта в том, что здесь одновременно работают роботическая бетонная печать, цифровая сборка деревянных элементов, вычислительно оптимизированные перекрытия и лёгкая высокоэффективная оболочка, превращая экспериментальную исследовательскую архитектуру в реально заселённое многоэтажное здание.',
        'image_urls': val['dfab_house']['ok_images'][:5],
    },
    {
        'title': 'Maslak No.1 Office Tower / EAA - Emre Arolat Architecture',
        'slug': 'maslak_no1_office_tower',
        'source_url': 'https://www.archdaily.com/800160/maslak-n-office-tower-emre-arolat-architects',
        'canonical_source_url': 'https://www.archdaily.com/800160/maslak-n-office-tower-emre-arolat-architects',
        'caption_ru': 'Maslak No.1 Office Tower\n\nЛокация: Стамбул, Турция\nАрхитектор: EAA - Emre Arolat Architecture\nГод реализации: 2014\nМатериалы: основное офисное ядро из reinforced concrete, базовая operable aluminum framing and glazing system, вторичная free-formed steel facade, curvilinear glazing modules размером 150 x 200 см, fish-scale стеклянные панели с translucent film разной степени прозрачности и буферные пространства с вертикальными садами между двумя оболочками.\nКратко: башня у магистрали Меджидиекёй–Маслак превращает обычный прямоугольный офисный объём в сложную климатическую машину с двойной оболочкой и вертикальными садами. Параметрическая логика здесь проявляется не как декоративный приём, а как способ настроить глубину фасада, степень прозрачности, акустический комфорт и экологическую работу высотного офиса в плотной городской среде.',
        'image_urls': val['maslak_no1']['ok_images'][:5],
    },
    {
        'title': '30 St Mary Axe Tower / Foster + Partners',
        'slug': 'thirty_st_mary_axe_tower',
        'source_url': 'https://www.archdaily.com/928285/30-st-mary-axe-tower-foster-plus-partners',
        'canonical_source_url': 'https://www.archdaily.com/928285/30-st-mary-axe-tower-foster-plus-partners',
        'caption_ru': '30 St Mary Axe Tower\n\nЛокация: Лондон, Великобритания\nАрхитектор: Foster + Partners\nГод реализации: 2003\nМатериалы: наружная оболочка из 5 500 треугольных и ромбовидных стеклянных панелей, double-glazed outer layer и single-glazed inner screen с центральной ventilated cavity и solar-control blinds, openable double-glazed panels в спиральных light-wells, external diagonal steel structure и крупноформатные extruded aluminium panels в интерьере входного уровня.\nКратко: башня Swiss Re остаётся одним из ключевых реализованных примеров того, как параметрическое компьютерное моделирование меняет не только образ небоскрёба, но и его экологическую логику. Аэродинамическая форма, спиральные световые шахты и вентилируемая фасадная система здесь собраны в цельную высотную типологию, где цифровая геометрия напрямую работает на естественное освещение, вентиляцию и снижение энергопотребления.',
        'image_urls': val['thirty_st_mary_axe']['ok_images'][:5],
    },
    {
        'title': 'Hospital Manta / PMMT',
        'slug': 'hospital_manta',
        'source_url': 'https://www.archdaily.com/928430/hospital-manta-pmmt',
        'canonical_source_url': 'https://www.archdaily.com/928430/hospital-manta-pmmt',
        'caption_ru': 'Hospital Manta\n\nЛокация: Манта, Эквадор\nАрхитектор: PMMT\nГод реализации: 2018\nМатериалы: сейсмостойкая фасадная система из polycarbonate panels, articulated joint technology со spring system для отделения деформаций каркаса от фасада и carpentry, а также набор специализированных компонентов от Parklex Prodema, Technal, RENSON, Saint-Gobain и Sabic.\nКратко: больница в Манте была построена после разрушительного землетрясения 2016 года и показывает, как параметрическое проектирование может работать в критической социальной инфраструктуре. Проект ценен тем, что объединяет гибкую медицинскую программу, ускоренные методы реализации и высокоадаптивную сейсмостойкую оболочку, где геометрия, узлы и материал фасада нацелены на устойчивость, скорость строительства и долгосрочную эксплуатационную надёжность.',
        'image_urls': val['hospital_manta']['ok_images'][:5],
    },
    {
        'title': 'Da Nang Hi-Tech Park Headquarters Building / HUNI Architectes',
        'slug': 'da_nang_hitech_park_hq',
        'source_url': 'https://www.archdaily.com/1027308/da-nang-hi-tech-park-headquarters-building-huni-architectes',
        'canonical_source_url': 'https://www.archdaily.com/1027308/da-nang-hi-tech-park-headquarters-building-huni-architectes',
        'caption_ru': 'Da Nang Hi-Tech Park Headquarters Building\n\nЛокация: Дананг, Вьетнам\nАрхитектор: HUNI Architectes\nГод реализации: 2020\nКратко: административный центр технологического парка организован как пересечение круговых объёмов и внутренних пустот, вдохновлённых одновременно шестернями и cloud-инфраструктурой. Для канала объект особенно важен своей data-driven климатической логикой: форма здания и параметрическая система солнцезащитных рёбер были разработаны через energy simulation, чтобы уменьшить перегрев и блики, сохранить естественный свет и придать фасаду непрерывный волнообразный ритм.',
        'image_urls': val['da_nang_hitech_hq']['ok_images'][:5],
    },
    {
        'title': 'Malta Maritime Trade Centre / AP Valletta',
        'slug': 'malta_maritime_trade_centre',
        'source_url': 'https://www.archdaily.com/502293/malta-maritime-trade-centre-architecture-project',
        'canonical_source_url': 'https://www.archdaily.com/502293/malta-maritime-trade-centre-architecture-project',
        'caption_ru': 'Malta Maritime Trade Centre\n\nЛокация: Марса, Мальта\nАрхитектор: AP Valletta\nГод реализации: 2007\nМатериалы: наружные metal louvered screens из anodized aluminium с цилиндрами диаметром 30 мм, вертикальным шагом 100 мм, framing с интервалом 1 м и горизонтальными обслуживающими walkway в зазоре 650 мм между экраном и фасадом.\nКратко: морской торговый центр интересен как ранний пример того, как параметрические исследования превращаются в конкретную рабочую фасадную систему большого офисного комплекса. Геометрия алюминиевых экранов была рассчитана так, чтобы одновременно сохранить виды на гавань, сократить солнечную нагрузку до 60 процентов на южных фасадах и снизить пиковый спрос на охлаждение, то есть фасад здесь спроектирован как точный экологический инструмент.',
        'image_urls': val['malta_maritime_trade_centre']['ok_images'][:5],
    },
]

for obj in objects:
    (outdir / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(outdir)
for obj in objects:
    print(obj['slug'])
