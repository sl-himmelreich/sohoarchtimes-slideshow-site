import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
out_dir = base / 'today_batch_20260506_user_three'
out_dir.mkdir(parents=True, exist_ok=True)

payloads = [
    {
        'title': 'AD Classics: The Guggenheim Museum Bilbao / Gehry Partners',
        'slug': 'guggenheim-museum-bilbao-special',
        'source_url': 'https://www.archdaily.com/422470/ad-classics-the-guggenheim-museum-bilbao-frank-gehry',
        'canonical_source_url': 'https://www.archdaily.com/422470/ad-classics-the-guggenheim-museum-bilbao-frank-gehry',
        'caption_ru': 'Музей Гуггенхайма в Бильбао\nЛокация: Бильбао, Испания\nАрхитектор: Gehry Partners\nГод реализации: 1997\nМатериалы: архитектурный титан, стальной несущий каркас, стеклянные поверхности и каменная облицовка, собранные в сложную пространственную оболочку музея.\nМузей Гуггенхайма в Бильбао выступает переходным кейсом, в котором цифровая технология обеспечивает реализуемость пластической формы. Здание на берегу Нервьона собирает вихревую композицию объёмов вокруг большого светового атриума и показывает момент, когда вычислительные инструменты уже не просто сопровождают проектирование, а становятся условием воплощения новой архитектурной пластики в реальном строительстве.',
        'image_urls': [
            'https://images.adsttc.com/media/images/521f/a052/e8e4/4eb9/4a00/0034/large_jpg/Flickr_User_RonG8888.jpg?1377804365',
            'https://images.adsttc.com/media/images/521f/a05f/e8e4/4eb9/4a00/0035/large_jpg/Flickr_User_EEPaul.jpg?1377804376',
            'https://images.adsttc.com/media/images/521f/a06a/e8e4/4e56/b500/006a/large_jpg/Flickr_User_Michael_Jones_51.jpg?1377804383',
            'https://images.adsttc.com/media/images/521f/a06d/e8e4/4eb9/4a00/0036/large_jpg/Flickr_User_mimmyg.jpg?1377804390',
            'https://images.adsttc.com/media/images/521f/a073/e8e4/4ebd/9000/006a/large_jpg/Flickr_User_Viajar_sin_Destino.jpg?1377804398'
        ]
    },
    {
        'title': 'Global Center for Health Innovation',
        'slug': 'global-center-for-health-innovation-special',
        'source_url': 'https://lmnarchitects.com/project/cleveland-convention-center-civic-core',
        'canonical_source_url': 'https://lmnarchitects.com/project/cleveland-convention-center-civic-core',
        'caption_ru': 'Global Center for Health Innovation\nЛокация: Кливленд, США\nАрхитектор: LMN Architects / Robert P. Madison International\nГод реализации: 2013\nМатериалы: фасадная система из стеклянных и precast-concrete панелей, доведённая до изготовления через цифровую модель фасадного рисунка.\nGlobal Center for Health Innovation служит примером прямой связи генеративной модели и цифрового производства фасада в общественной функции. Для одного из ключевых элементов комплекса LMN Tech Studio перевела эскизный рисунок оконного паттерна в параметрическую модель, а затем в fabrication-ready набор стеклянных и precast-concrete панелей, превратив цифровую логику в реально построенную городскую оболочку.',
        'image_urls': [
            'https://lmnarchitects.com/wp-content/uploads/2021/12/Cleveland-Convention-Center-Civic-Core_480-2000x1334.jpg',
            'https://lmnarchitects.com/wp-content/uploads/2021/12/Cleveland-Convention-Center-Civic-Core_340-1335x2000.jpg',
            'https://lmnarchitects.com/wp-content/uploads/2021/12/Cleveland-Convention-Center-Civic-Core_475-2000x1334.jpg',
            'https://lmnarchitects.com/wp-content/uploads/2021/12/Cleveland-Convention-Center-Civic-Core_477-2000x1334.jpg',
            'https://lmnarchitects.com/wp-content/uploads/2021/12/Cleveland-Convention-Center-Civic-Core_318-2000x1344.jpg'
        ]
    },
    {
        'title': 'DFAB House / NCCR Digital Fabrication',
        'slug': 'dfab-house-special-repeat',
        'source_url': 'https://www.archdaily.com/942221/dfab-house-eth-zurich-plus-nccr-digital-fabrication',
        'canonical_source_url': 'https://www.archdaily.com/942221/dfab-house-eth-zurich-plus-nccr-digital-fabrication',
        'caption_ru': 'DFAB House\nЛокация: Дюбендорф, Швейцария\nАрхитектор: ETH Zürich / NCCR Digital Fabrication\nГод реализации: 2019\nМатериалы: роботически изготовленные деревянные пространственные элементы, бетонные конструкции, элементы оболочки и остекления, а также экспериментальные узлы, собранные через цифровые строительные процессы.\nDFAB House представляет собой предельный современный кейс интеграции вычислительного проектирования и цифрового производства в полномасштабное здание. Это жилой исследовательский дом, где computational design, роботизированная сборка и 3D-печатно-ориентированные строительные процессы работают не как демонстрация отдельных фрагментов, а как целостная архитектурная система реального обитаемого объекта.',
        'image_urls': [
            'https://images.adsttc.com/media/images/5ef1/577d/b357/6529/f500/02f7/large_jpg/DFAB_HOUSE_11.jpg?1592874763',
            'https://images.adsttc.com/media/images/5ef1/5486/b357/658c/7f00/04d7/large_jpg/DFAB_HOUSE_16.jpg?1592874048',
            'https://images.adsttc.com/media/images/5ef1/5b40/b357/658c/7f00/04f3/large_jpg/DFAB_HOUSE_04.jpg?1592875782',
            'https://images.adsttc.com/media/images/5ef1/569f/b357/658c/7f00/04e3/large_jpg/DFAB_HOUSE_12.jpg?1592874607',
            'https://images.adsttc.com/media/images/5ef1/5516/b357/6529/f500/02ec/large_jpg/DFAB_HOUSE_15.jpg?1592874192'
        ]
    }
]

written = []
for payload in payloads:
    path = out_dir / f"{payload['slug']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    written.append(str(path))

print(json.dumps({'written': written}, ensure_ascii=False, indent=2))
