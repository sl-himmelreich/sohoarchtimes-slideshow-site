import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
outdir = base / 'today_batch_20260328'
outdir.mkdir(parents=True, exist_ok=True)
val = json.loads((base / 'image_validation_20260328.json').read_text(encoding='utf-8'))

objects = [
    {
        'title': 'Loop of Wisdom Museum & Reception Center / Powerhouse Company',
        'slug': 'loop_of_wisdom',
        'source_url': 'https://www.archdaily.com/949622/loop-of-wisdom-museum-powerhouse-company',
        'canonical_source_url': 'https://www.archdaily.com/949622/loop-of-wisdom-museum-powerhouse-company',
        'caption_ru': 'Loop of Wisdom Museum & Reception Center\n\nЛокация: Чэнду, Китай\nАрхитектор: Powerhouse Company\nГод реализации: 2020\nМатериалы: непрерывная кровельная оболочка с покрытием из rubber asphalt, 15 218 индивидуально профилированных алюминиевых плиток с нумерацией, структурное glazing высотой до 13 метров с glass reinforcement fins и деревянные потолки в выставочных пространствах.\nКратко: музей и приёмный центр в Chengdu Unis Chip City решён как непрерывное кольцо, которое следует рельефу участка и одновременно работает как общественный маршрут по кровле. Ценность проекта в том, что параметрическая геометрия здесь управляет не только пластикой формы, но и точной сборкой сложной алюминиевой оболочки, прозрачных фасадов и длинной пространственной последовательности, превращая здание в крупный цифрово спроектированный ландшафтный объект.',
        'image_urls': val['loop_of_wisdom']['ok_images'][:5],
    },
    {
        'title': 'Copyright Cloud Headquarter / HDD',
        'slug': 'copyright_cloud_headquarter',
        'source_url': 'https://www.archdaily.com/948109/copyright-cloud-headquarter-hdd',
        'canonical_source_url': 'https://www.archdaily.com/948109/copyright-cloud-headquarter-hdd',
        'caption_ru': 'Copyright Cloud Headquarter\n\nЛокация: Гуйян, Китай\nАрхитектор: HDD\nГод реализации: 2018\nМатериалы: curtain wall с белой каменной облицовкой на северном фасаде, стеклянные фасадные плоскости для объёма «smart information box» и алюминиевые ламели на северной и южной сторонах как ритмическая солнцезащитная система.\nКратко: штаб-квартира Copyright Cloud интерпретирует инфраструктуру больших данных как подвешенный цифровой объём, встроенный в сложный рельеф участка. Проект интересен тем, что образ «информационного бокса» переводится в архитектуру через сочетание приподнятой структуры, стеклянной оболочки и фасадных алюминиевых ритмов, создающих одновременно технологичный образ и рабочую климатическую оболочку.',
        'image_urls': val['copyright_cloud']['ok_images'][:5],
    },
    {
        'title': 'Computer History Museum / Mark Horton - Architecture',
        'slug': 'computer_history_museum',
        'source_url': 'https://www.archdaily.com/163795/computer-history-museum-mark-horton-architecture',
        'canonical_source_url': 'https://www.archdaily.com/163795/computer-history-museum-mark-horton-architecture',
        'caption_ru': 'Computer History Museum\n\nЛокация: Маунтин-Вью, Калифорния, США\nАрхитектор: Mark Horton - Architecture\nГод реализации: 2011\nКратко: реконструкция бывшего офисного здания Silicon Graphics превращает типовой корпоративный объём в музей вычислительной культуры с новым входным холлом, orientation theater, кафе, книжным магазином и крупным выставочным пространством. Для канала объект важен как архитектура внутри самой технологической экосистемы Кремниевой долины, где адаптивное переиспользование существующей оболочки стало пространственной рамкой для истории цифровой эпохи.',
        'image_urls': val['computer_history_museum']['ok_images'][:5],
    },
    {
        'title': 'Landesgartenschau Exhibition Hall / ICD/ITKE/IIGS University of Stuttgart',
        'slug': 'landesgartenschau_exhibition_hall',
        'source_url': 'https://www.archdaily.com/520897/landesgartenschau-exhibition-hall-icd-itke-iigs-university-of-stuttgart',
        'canonical_source_url': 'https://www.archdaily.com/520897/landesgartenschau-exhibition-hall-icd-itke-iigs-university-of-stuttgart',
        'caption_ru': 'Landesgartenschau Exhibition Hall\n\nЛокация: Швебиш-Гмюнд, Германия\nАрхитектор: ICD/ITKE/IIGS University of Stuttgart\nГод реализации: 2014\nМатериалы: первичная несущая оболочка из роботически префабрикованных пластин beech plywood толщиной 50 мм, 7 600 индивидуально изготовленных finger joints по кромкам элементов, цифрово префабрикованные слои insulation, waterproofing и cladding, а также повторное использование обрезков древесины в parquet flooring.\nКратко: выставочный павильон-холл стал одним из ранних полноразмерных доказательств того, как computational design, simulation и robotic fabrication могут прямо формировать несущую деревянную архитектуру. Здесь биомиметическая логика морских скелетных структур переведена в лёгкую пластинчатую систему, где конструкция, оболочка и производственный процесс проектируются как единая цифровая цепочка.',
        'image_urls': val['landesgartenschau']['ok_images'][:5],
    },
    {
        'title': 'New Science and Technology Museum of Henan Province / TJAD Atelier L+',
        'slug': 'henan_science_technology_museum',
        'source_url': 'https://www.archdaily.com/1034203/new-science-and-technology-museum-of-henan-province-tjad-atelier-l-plus',
        'canonical_source_url': 'https://www.archdaily.com/1034203/new-science-and-technology-museum-of-henan-province-tjad-atelier-l-plus',
        'caption_ru': 'New Science and Technology Museum of Henan Province\n\nЛокация: Чжэнчжоу, Китай\nАрхитектор: TJAD Atelier L+\nГод реализации: 2024\nМатериалы: двухслойная параметрически сгенерированная алюминиевая фасадная оболочка с fish-scale-like freeform рисунком, регулируемые aluminum panels, сложные curtain walls, стальной каркас с 80-метровыми truss bridges и трёхэтажный steel truss skybridge.\nКратко: крупный научно-технологический музей объединяет несколько тематических музеев в единую трёхлучевую композицию с гигантским атриумом и полноразмерной инженерной инфраструктурой. Особенно важен здесь уровень цифровой координации: форма, вентиляционная логика, фасадная геометрия и конструкция были синхронизированы через parametric simulations, wind tunnel testing, BIM и 3D scanning, что делает объект зрелым примером data-driven public architecture.',
        'image_urls': val['henan_museum']['ok_images'][:5],
    },
]

for obj in objects:
    (outdir / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(outdir)
for obj in objects:
    print(obj['slug'])
