import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
outdir = base / 'today_batch_20260327'
outdir.mkdir(parents=True, exist_ok=True)
val = json.loads((base / 'image_validation_20260327.json').read_text(encoding='utf-8'))

objects = [
    {
        'title': 'Communique Headquarters / DaeWha Kang Design',
        'slug': 'communique_headquarters',
        'source_url': 'https://www.archdaily.com/780596/communique-headquarters-daewha-kang-design',
        'canonical_source_url': 'https://www.archdaily.com/780596/communique-headquarters-daewha-kang-design',
        'caption_ru': 'Communique Headquarters\n\nЛокация: Сеул, Южная Корея\nАрхитектор: DaeWha Kang Design\nГод реализации: 2015\nМатериалы: гранитные панели, параметрически разбитые по искажённой ромбической сетке, зеркальные панели из нержавеющей стали в общественном подкарнизном пространстве и сплошное уличное glazing кафе от пола до потолка.\nКратко: реконструкция офисного здания 1980-х годов превращает обычный объём в выразительный адаптивный фасад, где одна и та же вычислительная сетка управляет панелизацией гранита, диагональным рисунком оконных переплётов и световым режимом интерьеров. Проект интересен тем, что алгоритмическая логика здесь работает одновременно как эстетическая система, как инструмент экономии материала и как способ улучшить инсоляцию и естественную вентиляцию рабочих пространств.',
        'image_urls': val['communique']['ok_images'][:5],
    },
    {
        'title': 'Bill & Melinda Gates Center for Computer Science & Engineering / LMN Architects',
        'slug': 'gates_center_cse',
        'source_url': 'https://www.archdaily.com/914647/bill-and-melinda-gates-center-for-computer-science-and-engineering-lmn-architects',
        'canonical_source_url': 'https://www.archdaily.com/914647/bill-and-melinda-gates-center-for-computer-science-and-engineering-lmn-architects',
        'caption_ru': 'Bill & Melinda Gates Center for Computer Science & Engineering\n\nЛокация: Сиэтл, США\nАрхитектор: LMN Architects\nГод реализации: 2018\nМатериалы: фасадная система из терракотовых панелей Gresmanc Group четырёх разных текстур, чёрное стекло и металлические солнцезащитные элементы, работающие как единая климатическая оболочка.\nКратко: учебно-исследовательский корпус для School of Computer Science & Engineering построен вокруг большого светового атриума, который связывает все этажи и делает здание социальным ядром кампуса. Особенно важен фасад, разработанный с использованием цифровых инструментов как высокопроизводительная оболочка: текстура, глубина и рисунок терракоты здесь одновременно регулируют солнечные нагрузки, прозрачность и визуальную идентичность здания.',
        'image_urls': val['gates']['ok_images'][:5],
    },
    {
        'title': 'MONOSPINAL Headquarters Office Building / Makoto Yamaguchi Design',
        'slug': 'monospinal_headquarters',
        'source_url': 'https://www.archdaily.com/1016470/monospinal-headquarters-office-building-makoto-yamaguchi-design',
        'canonical_source_url': 'https://www.archdaily.com/1016470/monospinal-headquarters-office-building-makoto-yamaguchi-design',
        'caption_ru': 'MONOSPINAL Headquarters Office Building\n\nЛокация: Тайто, Япония\nАрхитектор: Makoto Yamaguchi Design\nГод реализации: 2023\nМатериалы: наружные наклонные стены из тонких алюминиевых пластин шириной около 100 мм, CFT-колонны по углам, transfer structure со story-high trusses и интегрированная инженерная KNX/DALI-система управления зданием.\nКратко: новая штаб-квартира игровой компании превращает офис в вертикальный ландшафт для креативной работы, где уровень приватности, света, шума и обзора меняется от этажа к этажу. Геометрия балконов и наклонных стен разработана параметрическим методом в Grasshopper для одновременной настройки защиты от прямого света, качества рассеянного освещения, ветрового захвата и акустической защиты от железной дороги рядом.',
        'image_urls': val['monospinal']['ok_images'][:5],
    },
    {
        'title': 'Revolving Bricks Office Building / A.P.Pars Architects & Associates',
        'slug': 'revolving_bricks_office_building',
        'source_url': 'https://www.archdaily.com/972761/revolving-bricks-office-building-appars-architects-and-associates',
        'canonical_source_url': 'https://www.archdaily.com/972761/revolving-bricks-office-building-appars-architects-and-associates',
        'caption_ru': 'Revolving Bricks Office Building\n\nЛокация: Арак, Иран\nАрхитектор: A.P.Pars Architects & Associates\nГод реализации: 2015\nМатериалы: кирпичная фасадная решётка с параметрически рассчитанным поворотом элементов, цветовые акценты на торцах кирпичей и внешняя оболочка, регулирующая приватность, свет и видимость.\nКратко: офисное здание отвечает на конфликт между рабочей программой и жилым окружением через кирпичный экран, который меняет рисунок при движении вдоль улицы и работает как климатический и визуальный фильтр. Здесь параметрическая геометрия применяется не ради жеста, а как инструмент настройки освещённости, приватности и городской коммуникации через пластичный brick envelope.',
        'image_urls': val['revolving']['ok_images'][:5],
    },
    {
        'title': 'Nation Office Building Intervention / TANK Architectes',
        'slug': 'nation_office_building_intervention',
        'source_url': 'https://www.archdaily.com/1026501/nation-office-building-intervention-tank-architectes',
        'canonical_source_url': 'https://www.archdaily.com/1026501/nation-office-building-intervention-tank-architectes',
        'caption_ru': 'Nation Office Building Intervention\n\nЛокация: Париж, Франция\nАрхитектор: TANK Architectes\nГод реализации: 2024\nМатериалы: несущая и фасадная система из светло-серого бетона, уложенного горизонтальными слоями, крупные bow windows и прозрачные витражные плоскости, работающие на глубину, отражение и световой рельеф фасада.\nКратко: новое офисное здание у Place de la Nation встроено в хауссмановский контекст через выверенные пропорции и современную материальную логику. Проект интересен тем, что сочетает строгую городскую композицию с биофильной рабочей средой, террасами, естественным светом и фасадом, где бетонные слои и стекло создают тихую, но очень точную современную интерпретацию парижского каменного города.',
        'image_urls': val['nation']['ok_images'][:5],
    },
    {
        'title': 'Office Building Principe Amedeo 5 / Vittorio Grassi Architetto & Partners',
        'slug': 'principe_amedeo_5',
        'source_url': 'https://www.archdaily.com/956729/office-building-principe-amedeo-5-vittorio-grassi-architetto-and-partners',
        'canonical_source_url': 'https://www.archdaily.com/956729/office-building-principe-amedeo-5-vittorio-grassi-architetto-and-partners',
        'caption_ru': 'Office Building Principe Amedeo 5\n\nЛокация: Милан, Италия\nАрхитектор: Vittorio Grassi Architetto & Partners\nГод реализации: 2019\nМатериалы: curtain walls из laminated beech wood, selective screen-printed glass с декоративным parametric motif, суперизоляционные узлы оболочки, roof-integrated photovoltaic panels, basalt floors и дубовые порталы в общественных пространствах.\nКратко: реконструкция бывшей штаб-квартиры американского консульства превращает исторический миланский дворец в современное офисное здание с садом, прозрачным двусветным объёмом во дворе и новым attic floor на кровле. Особенно ценно здесь то, как параметрический орнамент стеклянной оболочки соединён с задачами энергоэффективности, а историческая ткань здания — с новой рабочей инфраструктурой и LEED Gold-ориентированной экологической стратегией.',
        'image_urls': val['principe_amedeo']['ok_images'][:5],
    }
]

for obj in objects:
    (outdir / f"{obj['slug']}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(outdir)
for obj in objects:
    print(obj['slug'])
