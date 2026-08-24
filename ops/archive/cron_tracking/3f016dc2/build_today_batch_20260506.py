import json
from pathlib import Path

base = Path('/home/user/workspace/cron_tracking/3f016dc2')
out_dir = base / 'today_batch_20260506'
out_dir.mkdir(parents=True, exist_ok=True)

payloads = [
    {
        'title': 'X Museum / Studio NOR',
        'slug': 'x-museum-beijing',
        'source_url': 'https://www.archdaily.com/1024371/x-museum-studio-nor',
        'canonical_source_url': 'https://www.archdaily.com/1024371/x-museum-studio-nor',
        'caption_ru': 'X Museum\nЛокация: Пекин, Китай\nАрхитектор: Studio NOR\nГод реализации: 2023\nМатериалы: сохранённая краснокирпичная оболочка промышленного склада 1960-х годов, крупнопролётная стальная ферма светового фонаря, новые стеклянные и стальные вставки, а также подвесные выставочные рамы, независимые от исторических стен.\nМузей преобразует бывший текстильный склад в современное выставочное пространство с последовательностью залов под мощным верхним светом. Проект не стирает индустриальную память здания, а наслаивает на неё новую музейную инфраструктуру и превращает старую фабричную типологию в точный культурный инструмент.',
        'image_urls': [
            'https://images.adsttc.com/media/images/6750/c6e9/5cf5/0b27/8f9e/c5fc/large_jpg/x-museum-studio-nor_5.jpg?1733347067',
            'https://images.adsttc.com/media/images/6750/c6e9/c61c/4b01/8965/ede9/large_jpg/x-museum-studio-nor_4.jpg?1733347087',
            'https://images.adsttc.com/media/images/6750/c6e2/c61c/4b01/8965/ede2/large_jpg/x-museum-studio-nor_1.jpg?1733347173',
            'https://images.adsttc.com/media/images/6750/c6e6/c61c/4b01/8965/ede6/large_jpg/x-museum-studio-nor_7.jpg?1733347064',
            'https://images.adsttc.com/media/images/6750/c6e7/5cf5/0b27/8f9e/c5f9/large_jpg/x-museum-studio-nor_2.jpg?1733347070'
        ]
    },
    {
        'title': 'One Thousand Museum Residential Tower / Zaha Hadid Architects',
        'slug': 'one-thousand-museum-miami',
        'source_url': 'https://www.archdaily.com/934407/one-thousand-museum-zaha-hadid-architects',
        'canonical_source_url': 'https://www.archdaily.com/934407/one-thousand-museum-zaha-hadid-architects',
        'caption_ru': 'One Thousand Museum Residential Tower\nЛокация: Майами, Флорида, США\nАрхитектор: Zaha Hadid Architects\nГод реализации: 2020\nМатериалы: несущий экзоскелет из бетона с использованием glass fibre reinforced concrete form-work, оставленного в роли постоянной внешней оболочки, а также hurricane glazing на основе систем SentryGlas и Trosifol.\n62-этажная жилая башня у Museum Park построена как непрерывная пластическая структура, в которой внешний каркас одновременно формирует образ здания и работает на сопротивление ветровым и штормовым нагрузкам. Периметральная конструкция освобождает внутренние планы от лишних колонн и делает высотный объект одним из самых узнаваемых примеров параметрически читаемой башенной архитектуры Заха Хадид.',
        'image_urls': [
            'https://images.adsttc.com/media/images/5e55/1d99/6ee6/7e94/3b00/0110/large_jpg/11_ZHA_One_Thousand_Museum_Miami_%C2%A9Hufton_Crow.jpg?1582636376',
            'https://images.adsttc.com/media/images/5e55/1f55/6ee6/7e4e/7800/0290/large_jpg/26_ZHA_One_Thousand_Museum_Miami_%C2%A9Hufton_Crow.jpg?1582636836',
            'https://images.adsttc.com/media/images/5e55/229b/6ee6/7e4e/7800/029d/large_jpg/21_ZHA_One_Thousand_Museum_Miami_%C2%A9Hufton_Crow.jpg?1582637680',
            'https://images.adsttc.com/media/images/5e55/22d5/6ee6/7e94/3b00/011c/large_jpg/30_ZHA_One_Thousand_Museum_Miami_%C2%A9Hufton_Crow.jpg?1582637731',
            'https://images.adsttc.com/media/images/5e55/1e66/6ee6/7e4e/7800/0289/large_jpg/08_ZHA_One_Thousand_Museum_Miami_%C2%A9Hufton_Crow.jpg?1582636606'
        ]
    },
    {
        'title': 'World Trade Center Transportation Hub / Santiago Calatrava',
        'slug': 'world-trade-center-transportation-hub-new-york',
        'source_url': 'https://www.archdaily.com/783965/world-trade-center-transportation-hub-santiago-calatrava',
        'canonical_source_url': 'https://www.archdaily.com/783965/world-trade-center-transportation-hub-santiago-calatrava',
        'caption_ru': 'World Trade Center Transportation Hub\nЛокация: Нью-Йорк, США\nАрхитектор: Santiago Calatrava\nГод реализации: 2016\nМатериалы: повторяющиеся стальные несущие рёбра оболочки Oculus, железобетонные основания и ограждающие системы, работающие вместе с верхним световым разрезом большого центрального зала.\nТранспортный узел задуман как самостоятельная городская структура на уровне улицы, связывающая общественные пространства нижнего Манхэттена в непрерывный пешеходный маршрут. Его эллиптический зал с ритмической системой стальных рёбер превращает инфраструктурный объект в скульптурную архитектуру дневного света, движения и крупного городского масштаба.',
        'image_urls': [
            'https://images.adsttc.com/media/images/5850/5b9b/e58e/ce32/8a00/0004/large_jpg/SC_Oculus_019.jpg?1481661331',
            'https://images.adsttc.com/media/images/5850/5bcd/e58e/ce32/8a00/0005/large_jpg/SC_Oculus_023.jpg?1481661381',
            'https://images.adsttc.com/media/images/5850/5d09/e58e/ce89/4b00/0034/large_jpg/SC_Oculus_061.jpg?1481661696',
            'https://images.adsttc.com/media/images/5850/5c2a/e58e/ce32/8a00/0008/large_jpg/SC_Oculus_036.jpg?1481661472',
            'https://images.adsttc.com/media/images/5850/5cbc/e58e/ce89/4b00/0031/large_jpg/SC_Oculus_054.jpg?1481661620'
        ]
    }
]

written = []
for payload in payloads:
    path = out_dir / f"{payload['slug']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    written.append(str(path))

print(json.dumps({'written': written}, ensure_ascii=False, indent=2))
