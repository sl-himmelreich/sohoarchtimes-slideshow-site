import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
out_dir = base / 'today_batch_20260507_special_seven'
out_dir.mkdir(parents=True, exist_ok=True)

payloads = [
    {
        'title': "BMW 'Dynaform'",
        'slug': 'bmw-dynaform-pavilion-special',
        'source_url': 'https://www.bollinger-grohmann.com/en.projects.bmw-dynaform.html',
        'canonical_source_url': 'https://www.bollinger-grohmann.com/en.projects.bmw-dynaform.html',
        'caption_ru': "Павильон BMW Dynaform\nЛокация: Франкфурт-на-Майне, Германия\nАрхитектор: Bernhard Franken / Franken Architekten\nГод реализации: 2001\nМатериалы: двухкриволинейный стальной каркас, 15 сварных hollow beam Vierendeel girders, продольные жёсткие трубчатые связи и мембранная оболочка.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Это показательный объект раннего этапа параметрической архитектуры, где форма выводится из вычислительной симуляции, а не подгоняется под заранее заданный образ. Его ценность в том, что цифровой процесс здесь становится источником самого формообразования, а computer-aided design and manufacturing напрямую определяют архитектурную и конструктивную реализуемость павильона.",
        'image_urls': [
            'https://www.bollinger-grohmann.com/data/images/bg_project_pic/file/default/00063_bmw-dynaform_4_3d.20130118-111730.jpg',
            'https://www.bollinger-grohmann.com/data/images/bg_project_pic/file/default/00063_bmw-dynaform_5_bernhard-franken.20130118-111543.jpg',
            'https://www.bollinger-grohmann.com/data/images/bg_project_pic/file/default/fra00p063_bg_e3.2.14_aufbauinnen_bg.jpg',
            'https://www.bollinger-grohmann.com/data/images/bg_project_pic/file/default/fra00p063_bg_e301-07-05dsc00036.jpg',
            'https://www.bollinger-grohmann.com/data/images/bg_project_pic/file/default/fra00p063_bg_haraldkloft_e3.2.12_aufbau-gate.jpg'
        ]
    },
    {
        'title': 'The HydraPier Pavilion',
        'slug': 'hydrapier-pavilion-special',
        'source_url': 'https://asymptote.net/projects/the-hydrapier-pavilion/',
        'canonical_source_url': 'https://asymptote.net/projects/the-hydrapier-pavilion/',
        'caption_ru': "HydraPier Pavilion\nЛокация: Харлеммермер, Нидерланды\nАрхитектор: Asymptote Architecture\nГод реализации: 2002\nМатериалы: doubly curved roof shells из single sheet-metal panels, изготовленных методом explosoform 2.5D panel moulding, и криволинейная стеклянная оболочка с использованием cold-bent glass.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Это один из первых общественных павильонов, в котором параметрическая геометрия была напрямую связана с технологиями изготовления. Проект важен как ранний пример единого контура, в котором проектирование и производство работают совместно, а архитектура, вода, свет и ландшафт собираются в одно вычислительно управляемое пространство.",
        'image_urls': [
            'https://asymptote.net/images/projects/the-hydrapier-pavilion/banner.jpg',
            'https://asymptote.net/images/projects/the-hydrapier-pavilion/exterior-waterfront.jpg',
            'https://asymptote.net/images/projects/the-hydrapier-pavilion/interior-exhibition.jpg',
            'https://asymptote.net/images/projects/the-hydrapier-pavilion/exterior-detail.jpg',
            'https://asymptote.net/images/projects/the-hydrapier-pavilion/exterior-night.jpg'
        ]
    },
    {
        'title': 'New Milan Trade Fair / Massimiliano & Doriana Fuksas',
        'slug': 'new-milan-trade-fair-special',
        'source_url': 'https://www.archdaily.com/248138/new-milan-trade-fair-studio-fuksas',
        'canonical_source_url': 'https://www.archdaily.com/248138/new-milan-trade-fair-studio-fuksas',
        'caption_ru': "New Milan Trade Fair\nЛокация: Ро-Перо, Италия\nАрхитектор: Massimiliano и Doriana Fuksas\nГод реализации: 2005\nМатериалы: стальная несущая система и свободноформная стеклянная оболочка, собранные в длинный общественный пассаж и сервисный центр комплекса.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Это значимый пример свободной оболочки начала XXI века, где сложная стеклянная структура стала возможна только за счёт тесной связи архитектурной, инженерной и производственной модели. Здесь цифровая среда уже не обслуживает форму, а удерживает всю систему как единое целое в масштабе крупного выставочного комплекса.",
        'image_urls': [
            'https://images.adsttc.com/media/images/5018/9ebe/28ba/0d5d/5d00/00ad/large_jpg/stringio.jpg?1414296347',
            'https://images.adsttc.com/media/images/5018/9ec2/28ba/0d5d/5d00/00ae/large_jpg/stringio.jpg?1414296334',
            'https://images.adsttc.com/media/images/5018/9ec4/28ba/0d5d/5d00/00af/large_jpg/stringio.jpg?1414296366',
            'https://images.adsttc.com/media/images/5018/9ec9/28ba/0d5d/5d00/00b0/large_jpg/stringio.jpg?1414296344',
            'https://images.adsttc.com/media/images/5018/9ece/28ba/0d5d/5d00/00b1/large_jpg/stringio.jpg?1414296363'
        ]
    },
    {
        'title': 'Aviva Stadium',
        'slug': 'aviva-stadium-special',
        'source_url': 'https://populous.com/showcases/aviva-stadium',
        'canonical_source_url': 'https://populous.com/showcases/aviva-stadium',
        'caption_ru': "Aviva Stadium\nЛокация: Дублин, Ирландия\nАрхитектор: Populous / Buro Happold\nГод реализации: 2010\nМатериалы: прозрачный фасад из polycarbonate louvres и стекла, suspended horseshoe roof и согласованная несущая и оболочечная система, разработанная в общей цифровой модели.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Это один из наиболее ясных примеров зрелой цифровой координации в общественном здании. Параметрическая модель здесь одновременно работает как инструмент формообразования, инженерной проверки, фасадной разработки и согласования между участниками проекта, а светочувствительная shingle-оболочка делает эту цифровую логику видимой в городском масштабе.",
        'image_urls': [
            'https://populous.com/uploads/2018/01/1839_229Dr.jpg',
            'https://populous.com/uploads/2018/01/Aviva_2.jpeg',
            'https://populous.com/uploads/2018/01/1839_104D.jpg',
            'https://populous.com/uploads/2018/01/05_2021_00_N59.jpg',
            'https://populous.com/uploads/2018/01/Aviva_Stadium_Header_Mobile.jpg'
        ]
    },
    {
        'title': 'Metropol Parasol',
        'slug': 'metropol-parasol-special',
        'source_url': 'https://jmayerh.de/metropol-parasol/',
        'canonical_source_url': 'https://jmayerh.de/metropol-parasol/',
        'caption_ru': "Metropol Parasol\nЛокация: Севилья, Испания\nАрхитектор: J. Mayer H. und Partner / Arup\nГод реализации: 2011\nМатериалы: bonded timber-construction с полиуретановым покрытием, собранная как одна из крупнейших инновационных деревянных оболочек своего времени.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Проект показывает, как цифровые методы могут соединить сложную деревянную геометрию, изготовление тысяч уникальных элементов и городскую общественную функцию. В итоге архитектурная форма работает не только как объект, но и как часть городской инфраструктуры — с рынком, музеем, площадями и маршрутами над археологическим слоем города.",
        'image_urls': [
            'https://jmayerh.de/files/2020/05/parasoles-fernandoalda-22-m-2-2560x1707.jpg',
            'https://jmayerh.de/files/2020/05/huftoncrow-metropol-parasol-35-2560x2389.jpg',
            'https://jmayerh.de/files/2020/05/huftoncrow-metropol-parasol-34-2560x1707.jpg',
            'https://jmayerh.de/files/2020/05/fernando-alda-riots-17-2560x2186.jpg',
            'https://jmayerh.de/files/2020/05/parasol-franck0860-2560x1917.jpg'
        ]
    },
    {
        'title': 'Heydar Aliyev Center / Zaha Hadid Architects',
        'slug': 'heydar-aliyev-center-special-repeat',
        'source_url': 'https://www.archdaily.com/448774/heydar-aliyev-center-zaha-hadid-architects',
        'canonical_source_url': 'https://www.archdaily.com/448774/heydar-aliyev-center-zaha-hadid-architects',
        'caption_ru': "Центр Гейдара Алиева\nЛокация: Баку, Азербайджан\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2013\nМатериалы: стекло, сталь, железобетон и сложная панельная оболочка непрерывной поверхности.\nПример параметрической архитектуры задолго до того, как в Москве её окрестили «эмо-теком». Это один из самых узнаваемых примеров непрерывной архитектурной поверхности, где здание, ландшафт и общественное пространство читаются как единая пластическая лента. Важную роль здесь играет и цифрово рассчитанная система швов и панелей, которая одновременно решает технические и композиционные задачи, удерживая непрерывность формы в масштабе большого культурного центра.",
        'image_urls': [
            'https://images.adsttc.com/media/images/5285/1f2b/e8e4/4e52/4b00/01ab/large_jpg/HAC_photo_by_Iwan_Baan_(2).jpg?1384455904',
            'https://images.adsttc.com/media/images/5285/1fce/e8e4/4e22/2500/0146/large_jpg/HAC_photo_by_Iwan_Baan_(8).jpg?1384456019',
            'https://images.adsttc.com/media/images/5285/2073/e8e4/4e8e/7200/015d/large_jpg/HAC_photo_by_Iwan_Baan_(3).jpg?1384456222',
            'https://images.adsttc.com/media/images/5285/2503/e8e4/4e52/4b00/01b8/large_jpg/HAC_Interior_photo_by_Hufton_Crow_(7).jpg?1384457412',
            'https://images.adsttc.com/media/images/5285/2329/e8e4/4e22/2500/014d/large_jpg/HAC_photo_by_Helene_Binet_03.jpg?1384456880'
        ]
    },
    {
        'title': 'National Taichung Theater',
        'slug': 'national-taichung-theater-special',
        'source_url': 'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/2015-p_04_en.html',
        'canonical_source_url': 'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/2015-p_04_en.html',
        'caption_ru': "Национальный театр Тайчжуна\nЛокация: Тайчжун, Тайвань\nАрхитектор: Toyo Ito & Associates / Arup\nГод реализации: 2016\nМатериалы: монолитная железобетонная структура, организованная как непрерывная система криволинейных полостей и поверхностей.\nЭто яркий пример того, как вычислительное проектирование может быть доведено до сложной бетонной реализации. Проект ценен тем, что соединяет топологически непрерывную форму, нестандартное производство и точную инженерную координацию в единой пространственной системе, где архитектура читается как сеть пещерообразных объёмов, собранных в полноценное общественное здание.",
        'image_urls': [
            'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/main%20photo_800.jpg',
            'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/1_800.jpg',
            'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/2_800.jpg',
            'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/3_800.jpg',
            'http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/4_800.jpg'
        ]
    }
]

written=[]
for payload in payloads:
    path=out_dir / f"{payload['slug']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    written.append(str(path))

print(json.dumps({'written': written}, ensure_ascii=False, indent=2))
