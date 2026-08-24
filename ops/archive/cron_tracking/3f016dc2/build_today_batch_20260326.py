import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
batch = base / 'today_batch_20260326'
batch.mkdir(parents=True, exist_ok=True)

sources = {
    'heydar': Path('/home/user/workspace/tool_calls/browser_task/output_mn72k4ch.json'),
    'nation': Path('/home/user/workspace/tool_calls/browser_task/output_mn72k4uf.json'),
    'connor': Path('/home/user/workspace/tool_calls/browser_task/output_mn72jyzg.json'),
    'techcombank': Path('/home/user/workspace/tool_calls/browser_task/output_mn72sojo.json'),
    'cctv': Path('/home/user/workspace/tool_calls/browser_task/output_mn72vrif.json'),
}

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

heydar = load_json(sources['heydar'])
nation = load_json(sources['nation'])
connor = load_json(sources['connor'])
techcombank = load_json(sources['techcombank'])['candidates'][1]
cctv = load_json(sources['cctv'])['candidate']

objects = [
    {
        'title': heydar['title'],
        'slug': 'heydar_aliyev_cultural_center',
        'source_url': 'https://parametric-architecture.com/heydar-aliyev-cultural-center-study/',
        'canonical_source_url': 'https://parametric-architecture.com/heydar-aliyev-cultural-center-study/',
        'caption_ru': "Хейдар Алиев Центр\n\nЛокация: Баку, Азербайджан\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2012\nМатериалы: пространственный стальной каркас и бесшовная оболочка из панелей GFRC (glass fiber-reinforced concrete), которая объединяет кровлю, фасад и складки рельефа в единую непрерывную поверхность.\nКратко: культурный центр с библиотекой, музеем и аудиторией задуман как текучая общественная топография, где параметрическая геометрия превращает здание и ландшафт в одну связанную систему. Плавная белая оболочка формирует большие безопорные пространства и стала одной из самых узнаваемых реализаций параметрической архитектуры начала XXI века.",
        'image_urls': heydar['image_urls'],
    },
    {
        'title': nation['title'],
        'slug': 'nation_office_building_intervention_tank',
        'source_url': 'https://www.archdaily.com/1026501/nation-office-building-intervention-tank-architectes',
        'canonical_source_url': 'https://www.archdaily.com/1026501/nation-office-building-intervention-tank-architectes',
        'caption_ru': "Nation Office Building Intervention\n\nЛокация: Париж, Франция\nАрхитектор: TANK Architectes\nГод реализации: 2024\nКратко: реконструкция и расширение офисного здания на Place de la Nation переосмысляет плотную парижскую городскую ткань через современную рабочую среду с террасами, балконами и озеленённой кровлей. Проект выстраивает точный диалог между хауссмановским окружением и новой архитектурой, усиливая естественное освещение, визуальные связи и коллективные пространства внутри объёма площадью около 7 700 м².",
        'image_urls': nation['image_urls'],
    },
    {
        'title': connor['title'],
        'slug': 'the_connor_group_corporate_headquarters',
        'source_url': 'https://www.archdaily.com/559061/corporate-headquarters-the-connor-group',
        'canonical_source_url': 'https://www.archdaily.com/559061/corporate-headquarters-the-connor-group',
        'caption_ru': "Corporate Headquarters / The Connor Group\n\nЛокация: Сентервилл, Огайо, США\nАрхитектор: Moody Nolan\nГод реализации: 2014\nМатериалы: фасадная система с облицовкой Alucobond, большие стеклянные плоскости, стальной каркас и тёплые деревянные поверхности в интерьере; общественное ядро собрано вокруг атриума с верхним светом.\nКратко: штаб-квартира площадью около 39 000 ft² отсылает к авиационному наследию места и организована вокруг светового атриума, который затягивает дневной свет глубоко в план. Треугольная пластика фасада и компактные офисные крылья формируют выразительный корпоративный объём, где все рабочие места получают естественное освещение и визуальную связь с ландшафтом.",
        'image_urls': connor['image_urls'],
    },
    {
        'title': techcombank['title'],
        'slug': 'techcombank_headquarters_hanoi',
        'source_url': techcombank['source_url'],
        'canonical_source_url': techcombank['canonical_source_url'],
        'caption_ru': "Techcombank Headquarters Hanoi\n\nЛокация: Ханой, Вьетнам\nАрхитектор: Foster + Partners\nГод реализации: 2023\nМатериалы: вычислительно спроектированные металлические солнцезащитные экраны и mesh-панели, стеклянная curtain wall верхних этажей, алюминиевые элементы фасадной системы и массивный городской подиум.\nКратко: 22-этажная штаб-квартира банка собирает ключевые функции компании рядом со Старым кварталом и соединяет масштаб небоскрёба с более камерной городской средой у основания. Нижние уровни закрыты тонко прорисованной экранной оболочкой, вдохновлённой плетением бамбука, а верхние этажи раскрываются как прозрачный офисный объём с видами на Hoan Kiem Lake и панораму Ханоя.",
        'image_urls': techcombank['image_urls'],
    },
    {
        'title': cctv['title'],
        'slug': 'cctv_headquarters_oma',
        'source_url': cctv['source_url'],
        'canonical_source_url': cctv['canonical_source_url'],
        'caption_ru': "CCTV Headquarters\n\nЛокация: Пекин, Китай\nАрхитекторы: OMA, Rem Koolhaas, Ole Scheeren\nГод реализации: 2012\nКратко: штаб-квартира China Central Television радикально переосмысливает типологию высотного здания, соединяя две наклонные башни в непрерывную пространственную петлю с консольным мостом. Диагональная фасадная сетка делает видимой работу сил внутри объёма: ячейки уплотняются в зонах максимальных напряжений и раскрываются там, где нагрузка меньше, превращая вычислительную структурную логику в главный образ здания.",
        'image_urls': cctv['image_urls'],
    },
]

for obj in objects:
    out = batch / f"{obj['slug']}.json"
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

print(str(batch))
for obj in objects:
    print(obj['slug'])
