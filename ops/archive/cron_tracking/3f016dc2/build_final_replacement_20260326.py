import json
from pathlib import Path

cand = json.loads(Path('/home/user/workspace/tool_calls/browser_task/output_mn734bve.json').read_text(encoding='utf-8'))['candidate']
obj = {
    'title': cand['title'],
    'slug': 'bund_finance_centre',
    'source_url': cand['source_url'],
    'canonical_source_url': cand['canonical_source_url'],
    'caption_ru': "Bund Finance Centre\n\nЛокация: Шанхай, Китай\nАрхитекторы: Foster + Partners, Heatherwick Studio\nГод реализации: 2017\nМатериалы: облицовка из тщательно обработанного гранита, стеклянные фасадные плоскости и кинетическая вуаль из 675 элементов из magnesium alloy, движущихся по трём независимым рельсам и работающих как изменяемая экранная оболочка.\nКратко: многофункциональный комплекс на набережной Бунда объединяет офисные башни, гостиницу, торговые пространства и культурный центр в ансамбль площадью около 420 000 м². Его главный образ формирует подвижная фасадная система, вдохновлённая традиционными китайскими головными украшениями: она меняет степень прозрачности, открывая и скрывая сценическое пространство и превращая вычислительно спроектированную кинетику в часть городской жизни здания.",
    'image_urls': cand['image_urls'],
}
base = Path('/home/user/workspace/cron_tracking/3f016dc2/today_batch_20260326')
(base / 'bund_finance_centre.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
print('bund_finance_centre')
