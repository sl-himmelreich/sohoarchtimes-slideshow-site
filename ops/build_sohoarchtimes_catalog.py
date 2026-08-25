import json
import re
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from PIL import Image

MSK = ZoneInfo('Europe/Moscow')
GRACE_HOURS = 12
NOW = datetime.now(MSK)

OPS = Path(__file__).resolve().parent            # ops/
ROOT = OPS.parent                                 # корень репо = папка сайта
OUT_DIR = OPS / 'site_data'
SITE_DIR = ROOT
RECOVERED_PAYLOADS = OUT_DIR / 'recovered_source_payloads.json'
PUBLISHER_PROOF = OPS / 'publisher_proof.json'   # ведётся ops/publish_album.py
SLIDE_BLOCKLIST = OUT_DIR / 'slide_blocklist.json'      # ручные исключения витрины
IMAGE_DIMENSIONS = OUT_DIR / 'image_dimensions.json'    # кэш {url: [w, h]}
IMAGE_ARCHIVE = OUT_DIR / 'image_archive.json'          # манифест архива кадров
OUT_DIR.mkdir(exist_ok=True)

# Собственный архив кадров витрины (ops/mirror_showcase_images.py): копии в
# бакете soho-archtimes-site под img/, раздаются через archtimes.sohoai.ru.
# Архивная копия ставится в url_fallback — если первоисточник умрёт или закроет
# хотлинк, сайт сам переключится на неё без потери качества.
ARCHIVE_BASE_URL = 'https://archtimes.sohoai.ru/'

# Правило качества витрины (CLAUDE.md, указание владельца 2026-08-25):
# никаких картинок меньше 1800 px по короткой стороне. Если основной URL мельче,
# сборщик пробует тот же кадр в большем размере (adsttc /original/); не дотянул —
# кадр с витрины снимается.
MIN_SHORT_SIDE = 1800

# Размерные варианты adsttc одного и того же кадра (один asset id и имя файла).
ADSTTC_SIZE_RE = re.compile(r'/(?:thumb_jpg|small_jpg|newsletter|medium_jpg|large_jpg|slideshow)/')

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})


def norm_ws(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').replace('\xa0', ' ')).strip()


def parse_caption(text: str):
    lines = [norm_ws(x) for x in text.splitlines() if norm_ws(x)]
    if not lines:
        return {}
    full_text = norm_ws(text)
    title = lines[0]
    location = ''
    architects = ''
    year = ''
    materials = ''
    description_parts = []
    field_mode = False
    for line in lines[1:]:
        if line.startswith('Локация:'):
            location = norm_ws(line.split(':', 1)[1])
            field_mode = True
        elif line.startswith('Архитектор:') or line.startswith('Архитекторы:'):
            architects = norm_ws(line.split(':', 1)[1])
            field_mode = True
        elif line.startswith('Год:') or line.startswith('Год реализации:'):
            year = norm_ws(line.split(':', 1)[1])
            field_mode = True
        elif line.startswith('Материалы:'):
            materials = norm_ws(line.split(':', 1)[1])
            field_mode = True
        elif line.startswith('Описание:'):
            description_parts.append(norm_ws(line.split(':', 1)[1]))
            field_mode = True
        else:
            # For older captions location may be plain line 2; for newer captions body may follow after fields.
            if not field_mode and not location:
                location = line
            else:
                description_parts.append(line)

    # Heuristic for old one-paragraph captions without explicit field labels.
    if not architects and not year and len(title) > 120:
        m = re.match(r'^(?P<title>[^,]+),\s*(?P<location>[^.]+?)\.\s*(?P<architects>.+?),\s*(?:реализация|ввод|открытие)\s*[—-]\s*(?P<year>\d{4})\s*год\.?\s*(?P<desc>.*)$', full_text)
        if m:
            title = norm_ws(m.group('title'))
            location = location or norm_ws(m.group('location'))
            architects = norm_ws(m.group('architects'))
            year = norm_ws(m.group('year'))
            if m.group('desc'):
                description_parts = [norm_ws(m.group('desc'))]

    description = norm_ws(' '.join(description_parts))
    overlay_parts = [title]
    if architects:
        overlay_parts.append(architects)
    if year:
        overlay_parts.append(year)
    if location:
        overlay_parts.append(location)
    overlay_text = ' / '.join(overlay_parts)
    return {
        'title': title,
        'location': location,
        'architects': architects,
        'year': year,
        'materials': materials,
        'description': description,
        'overlay_text': overlay_text,
    }
    

def extract_photos_and_caption(msg):
    photos = []
    photo_message_ids = []
    for a in msg.select('.tgme_widget_message_photo_wrap'):
        style = a.get('style', '')
        m = re.search(r"background-image:url\('([^']+)'\)", style)
        href = a.get('href') or ''
        if m:
            photos.append(m.group(1))
        m2 = re.search(r'/SohoArchTimes/(\d+)\?single', href)
        if m2:
            photo_message_ids.append(int(m2.group(1)))
    text_el = msg.select_one('.tgme_widget_message_text')
    caption = '\n'.join(text_el.stripped_strings) if text_el else ''
    return photos, photo_message_ids, caption


def fetch_public_posts():
    pages = []
    records = {}
    url = 'https://t.me/s/SohoArchTimes'
    seen_pages = set()
    while url and url not in seen_pages:
        seen_pages.add(url)
        html = SESSION.get(url, timeout=30).text
        pages.append(url)
        soup = BeautifulSoup(html, 'html.parser')
        for msg in soup.select('.tgme_widget_message[data-post]'):
            post = msg.get('data-post', '')
            if not post.startswith('SohoArchTimes/'):
                continue
            message_id = int(post.split('/')[-1])
            photos, photo_message_ids, caption = extract_photos_and_caption(msg)
            parsed = parse_caption(caption)
            prev = records.get(message_id, {})
            prev_photos = prev.get('telegram_image_urls', [])
            best_photos = photos if len(photos) > len(prev_photos) else prev_photos
            best_photo_ids = photo_message_ids if len(photo_message_ids) > len(prev.get('photo_message_ids', [])) else prev.get('photo_message_ids', [])
            best_caption = caption if len(caption) > len(prev.get('caption_text', '')) else prev.get('caption_text', '')
            best_parsed = parsed if len(caption) > len(prev.get('caption_text', '')) else prev.get('parsed_caption', {})
            records[message_id] = {
                **prev,
                'message_id': message_id,
                'telegram_post_url': f'https://t.me/SohoArchTimes/{message_id}',
                'telegram_image_urls': best_photos,
                'photo_message_ids': best_photo_ids,
                'caption_text': best_caption,
                'parsed_caption': best_parsed,
            }
        more = soup.select_one('.tme_messages_more')
        url = urljoin('https://t.me', more.get('href')) if more and more.get('href') else None
    return {'pages': pages, 'records': records}


def _normalize_source_image_url(url: str) -> str:
    url = (url or '').strip()
    if not url:
        return ''
    url = url.replace('http://s3.amazonaws.com/images.adsttc.com/media/images/', 'https://images.adsttc.com/media/images/')
    url = url.replace('https://s3.amazonaws.com/images.adsttc.com/media/images/', 'https://images.adsttc.com/media/images/')
    url = re.sub(r'/((?:small|medium|newsletter|thumb)_jpg)/', '/large_jpg/', url)
    return url


def _is_invalid_source_image_url(url: str) -> bool:
    low = (url or '').strip().lower()
    if not low.startswith('http://') and not low.startswith('https://'):
        return True
    banned_parts = [
        'assets.adsttc.com',
        '/doodles/',
        '/og/flat/',
        '/bio_photo/',
    ]
    if any(part in low for part in banned_parts):
        return True
    if 'parametric-architecture.com' in low and '/wp-content/uploads/' not in low:
        return True
    if 'images.adsttc.com' in low and '/media/images/' not in low:
        return True
    return False


def _sanitize_image_urls(urls):
    cleaned = []
    seen = set()
    for raw in urls or []:
        url = _normalize_source_image_url(raw)
        if not url or _is_invalid_source_image_url(url) or url in seen:
            continue
        seen.add(url)
        cleaned.append(url)
    return cleaned


def _sanitize_telegram_image_urls(urls):
    """Filter Telegram image URLs to keep only stable, public-channel-faithful ones.

    - ``cdn*.telesco.pe`` and ``cdn-telegram.org`` URLs (from the public t.me/s preview)
      are stable and identical to what the public channel displays.
    - ``api.telegram.org/file/bot...`` URLs expire and must NEVER be rendered.
    """
    cleaned = []
    seen = set()
    for raw in urls or []:
        url = (raw or '').strip()
        if not url:
            continue
        low = url.lower()
        if not (low.startswith('http://') or low.startswith('https://')):
            continue
        if 'api.telegram.org/file/bot' in low:
            # Expiring bot file URL — refuse.
            continue
        if url in seen:
            continue
        seen.add(url)
        cleaned.append(url)
    return cleaned


def build_publisher_proof_index():
    """Return {message_id: {'image_urls': [...], 'source_url': ..., 'title': ...}}.

    ops/publisher_proof.json is the ONLY source of truth for which exact
    image URLs were actually uploaded to a given Telegram message:
    publish_album.py appends an entry there on every successful publish
    (историческая часть восстановлена единожды из ops/archive при миграции
    2026-08-24). Rendering those URLs is faithful in content; only the
    resolution differs upward versus the t.me/s preview.
    """
    if not PUBLISHER_PROOF.exists():
        return {}
    try:
        raw = json.loads(PUBLISHER_PROOF.read_text())
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    proof = {}
    for key, data in raw.items():
        if not isinstance(data, dict):
            continue
        try:
            mid = int(data.get('message_id') or key)
        except Exception:
            continue
        urls = [u for u in (data.get('image_urls') or []) if isinstance(u, str) and u]
        if not urls:
            continue
        proof[mid] = {
            'image_urls': urls,
            'source_url': data.get('source_url', ''),
            'title': data.get('title', ''),
        }
    return proof


def load_slide_blocklist():
    """{(mid, idx), ...} — кадры, вручную снятые с витрины.

    ops/site_data/slide_blocklist.json ведётся руками: кадры, где нет
    архитектуры (пейзажи-референсы, чертежи, фото стройки). Telegram не
    трогается — исключение действует только на slides.json.
    """
    if not SLIDE_BLOCKLIST.exists():
        return set()
    try:
        raw = json.loads(SLIDE_BLOCKLIST.read_text())
    except Exception:
        return set()
    blocked = set()
    for item in (raw.get('blocked') or []) if isinstance(raw, dict) else []:
        try:
            blocked.add((int(item['mid']), int(item['idx'])))
        except Exception:
            continue
    return blocked


def load_image_archive():
    """{source_url: {'key': 'img/<sha>.jpg', ...}} — см. ops/mirror_showcase_images.py."""
    if not IMAGE_ARCHIVE.exists():
        return {}
    try:
        raw = json.loads(IMAGE_ARCHIVE.read_text())
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def load_dimension_cache():
    if not IMAGE_DIMENSIONS.exists():
        return {}
    try:
        raw = json.loads(IMAGE_DIMENSIONS.read_text())
    except Exception:
        return {}
    cache = {}
    if isinstance(raw, dict):
        for url, wh in raw.items():
            if isinstance(wh, (list, tuple)) and len(wh) == 2:
                try:
                    cache[url] = (int(wh[0]), int(wh[1]))
                except Exception:
                    continue
    return cache


def measure_image(url, cache):
    """(w, h) картинки по URL; сначала кэш, иначе частичная докачка.

    Читаем поток кусками и пробуем распарсить заголовок — для JPEG размер
    обычно известен по первым десяткам килобайт, качать файл целиком не надо.
    Не смогли измерить — возвращаем None (кадр на витрину не пойдёт: качество
    не доказано).
    """
    if url in cache:
        return cache[url]
    buf = b''
    size = None
    try:
        with SESSION.get(url, timeout=30, stream=True) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(65536):
                buf += chunk
                try:
                    size = Image.open(BytesIO(buf)).size
                    break
                except Exception:
                    if len(buf) > 8 * 1024 * 1024:
                        break
    except Exception:
        size = None
    if size and size[0] > 0 and size[1] > 0:
        cache[url] = (int(size[0]), int(size[1]))
    return cache.get(url)


def meets_showcase_quality(width, height):
    return min(width, height) >= MIN_SHORT_SIDE


def highres_candidates(url):
    """URL-ы того же кадра в большем разрешении (тот же asset, другой размер).

    Для adsttc замена размерного сегмента на /original/ отдаёт исходник
    фотографии без уменьшения — содержание идентично, выше только разрешение.
    """
    if 'images.adsttc.com' in url and ADSTTC_SIZE_RE.search(url):
        return [ADSTTC_SIZE_RE.sub('/original/', url)]
    return []


def load_local_payloads():
    local = {}
    if RECOVERED_PAYLOADS.exists():
        try:
            recovered = json.loads(RECOVERED_PAYLOADS.read_text())
        except Exception:
            recovered = {}
        if isinstance(recovered, dict):
            for key, data in recovered.items():
                if not isinstance(data, dict):
                    continue
                try:
                    message_id = int(data.get('message_id') or key)
                except Exception:
                    continue
                source_image_urls = _sanitize_image_urls(data.get('source_image_urls') or [])
                if len(source_image_urls) < 5:
                    continue
                existing = local.get(message_id, {})
                local[message_id] = {
                    'message_id': message_id,
                    'title': existing.get('title') or data.get('title', ''),
                    'slug': existing.get('slug', '') or data.get('slug', ''),
                    'source_url': existing.get('source_url') or data.get('source_url', ''),
                    'canonical_source_url': existing.get('canonical_source_url') or data.get('canonical_source_url', ''),
                    'source_image_urls': source_image_urls,
                    'caption_text_local': existing.get('caption_text_local', ''),
                    'parsed_local': existing.get('parsed_local', {}),
                }
    return local


def load_registry():
    p = OPS / 'published_objects.json'
    data = json.loads(p.read_text())
    reg = {}
    for item in data:
        mid = item.get('telegram_message_id')
        if not mid:
            continue
        reg[int(mid)] = item
    return reg


def _published_at_msk(reg):
    dt_text = (reg or {}).get('datetime_published_to_telegram', '')
    if dt_text:
        try:
            dt = datetime.fromisoformat(dt_text)
            return dt if dt.tzinfo else dt.replace(tzinfo=MSK)
        except Exception:
            pass
    date_text = (reg or {}).get('date_published_to_telegram', '')
    if date_text:
        try:
            return datetime.fromisoformat(date_text).replace(tzinfo=MSK, hour=9, minute=0, second=0, microsecond=0)
        except Exception:
            return None
    return None


def _within_grace_window(reg):
    published_at = _published_at_msk(reg)
    if not published_at:
        return False
    return NOW < (published_at + timedelta(hours=GRACE_HOURS))


def _merge_parsed(public_parsed, local_parsed):
    public_parsed = public_parsed or {}
    local_parsed = local_parsed or {}
    merged = {}
    for key in ['title', 'location', 'architects', 'year', 'materials', 'description', 'overlay_text']:
        merged[key] = public_parsed.get(key) or local_parsed.get(key) or ''
    return merged


def merge_records(public_records, local_payloads, registry, publisher_proof):
    all_ids = sorted(set(public_records) | set(local_payloads) | set(registry))
    posts = []
    for mid in all_ids:
        public = public_records.get(mid, {})
        local = local_payloads.get(mid, {})
        reg = registry.get(mid, {})
        is_public = mid in public_records
        within_grace = _within_grace_window(reg)
        published_at = _published_at_msk(reg)

        # New Telegram posts should appear on the site only after the 12-hour review window.
        if published_at and within_grace:
            continue
        if not is_public:
            continue

        parsed = _merge_parsed(public.get('parsed_caption'), local.get('parsed_local'))
        parsed_title = parsed.get('title') or ''
        registry_title = reg.get('title') or local.get('title') or ''
        if registry_title and (not parsed_title or len(parsed_title) > 120):
            title = registry_title
        else:
            title = parsed_title or registry_title or ''
        telegram_preview_images = _sanitize_telegram_image_urls(public.get('telegram_image_urls') or [])
        telegram_full_images = _sanitize_telegram_image_urls(reg.get('telegram_full_image_urls') or [])
        source_images = _sanitize_image_urls(local.get('source_image_urls') or [])

        # ---- Image source decision ------------------------------------------------
        # Tier A — PROVEN HIGH-RES: we have a publish_results entry that
        # binds a payload file to this Telegram message_id, the payload's
        # image_urls survived locally, AND the upload count matches the
        # public Telegram preview count. In that case the publisher's
        # original URLs are the *exact* images uploaded to Telegram, just
        # at higher resolution than the t.me/s preview JPEG (the previews
        # are downsized by Telegram). Rendering those URLs is faithful in
        # content; only the resolution differs upward.
        #
        # Tier B — TELEGRAM PREVIEW: fall back to the public cdn*.telesco.pe
        # preview URLs. These are exactly what t.me/s/SohoArchTimes serves
        # but are downsized to ~800px and look soft on large displays.
        #
        # Tier C — TELEGRAM FULL STABLE: only stable telesco.pe full URLs
        # are accepted. Bot-API file URLs are refused (they expire).
        #
        # Tier D — HIDDEN: no Telegram-faithful imagery; post is hidden.
        #
        # Recovered/heuristic ``source_image_urls`` (e.g. ArchDaily gallery
        # walks) are NEVER used as a render source on their own — we cannot
        # prove they match what the bot uploaded.
        proof = publisher_proof.get(mid)
        proven_image_urls = []
        if proof:
            sanitized = _sanitize_image_urls(proof.get('image_urls') or [])
            # We require the publisher upload count to match the public
            # preview count. If counts disagree (e.g. retry partially failed),
            # we refuse the high-res swap to avoid silently substituting an
            # image set that does not match what is in the channel.
            if sanitized and telegram_preview_images and len(sanitized) == len(telegram_preview_images):
                proven_image_urls = sanitized

        image_urls_fallback = []
        if proven_image_urls:
            image_urls = proven_image_urls
            image_urls_fallback = telegram_preview_images
            image_source_type = 'proven_high_res'
        elif telegram_preview_images:
            image_urls = telegram_preview_images
            image_source_type = 'telegram_preview'
        else:
            stable_full = [u for u in telegram_full_images if 'telesco.pe' in u or 'cdn-telegram.org' in u]
            if stable_full:
                image_urls = stable_full
                image_source_type = 'telegram_full_stable'
            else:
                image_urls = []
                image_source_type = 'hidden_no_telegram_images'

        if not image_urls:
            continue
        post = {
            'message_id': mid,
            'telegram_post_url': public.get('telegram_post_url') or reg.get('canonical_url') or f'https://t.me/SohoArchTimes/{mid}',
            'source_url': local.get('source_url') or reg.get('source_url') or (proof.get('source_url') if proof else ''),
            'canonical_source_url': local.get('canonical_source_url') or reg.get('canonical_source_url') or '',
            'title': title,
            'location': parsed.get('location', ''),
            'architects': parsed.get('architects', ''),
            'year': parsed.get('year', ''),
            'materials': parsed.get('materials', ''),
            'description': parsed.get('description', ''),
            'overlay_text': (' / '.join([x for x in [title, parsed.get('architects', ''), parsed.get('year', ''), parsed.get('location', '')] if x]) or title),
            'caption_text': public.get('caption_text') or local.get('caption_text_local') or '',
            'telegram_image_urls': telegram_preview_images,
            'telegram_full_image_urls': telegram_full_images,
            'source_image_urls': source_images,
            'image_urls': image_urls,
            'image_urls_fallback': image_urls_fallback,
            'image_source_type': image_source_type,
            'has_publisher_proof': bool(proof),
            'photo_message_ids': public.get('photo_message_ids', []),
            'is_publicly_visible': is_public,
            'within_grace_window': within_grace,
            'published_at_msk': published_at.isoformat() if published_at else '',
        }
        posts.append(post)
    # CLAUDE.md: сортировка newest first по message_id; внутри поста порядок
    # изображений сохраняет flatten_slides (idx по возрастанию).
    posts.sort(key=lambda x: x['message_id'], reverse=True)
    return posts


def flatten_slides(posts):
    slides = []
    for post in posts:
        fallback_urls = post.get('image_urls_fallback') or []
        for idx, image_url in enumerate(post['image_urls'], start=1):
            fallback_url = ''
            if 0 < idx <= len(fallback_urls):
                fallback_url = fallback_urls[idx - 1]
            slides.append({
                'slide_id': f"{post['message_id']}-{idx}",
                'message_id': post['message_id'],
                'index_in_post': idx,
                'title': post['title'],
                'architects': post['architects'],
                'year': post['year'],
                'location': post['location'],
                'overlay_text': post['overlay_text'],
                'image_url': image_url,
                'image_url_fallback': fallback_url,
                'telegram_post_url': post['telegram_post_url'],
                'image_source_type': post['image_source_type'],
            })
    return slides


def main():
    public = fetch_public_posts()
    local_payloads = load_local_payloads()
    registry = load_registry()
    publisher_proof = build_publisher_proof_index()
    posts = merge_records(public['records'], local_payloads, registry, publisher_proof)
    slides = flatten_slides(posts)
    public_ids = set(public['records'])
    pending_grace_posts = sorted(mid for mid, reg in registry.items() if _within_grace_window(reg))
    build_version = NOW.strftime('%Y%m%dT%H%M%S')
    posts_hidden_no_telegram_images = sorted(
        mid for mid in (set(local_payloads) | set(registry))
        if mid in public['records']
        and not _sanitize_telegram_image_urls(public['records'][mid].get('telegram_image_urls') or [])
    )
    proven_posts = [p for p in posts if p['image_source_type'] == 'proven_high_res']
    proven_but_count_mismatch = sorted(
        mid for mid, proof in publisher_proof.items()
        if mid in public['records']
        and (mid in {p['message_id'] for p in posts})
        and not any(p['message_id'] == mid and p['image_source_type'] == 'proven_high_res' for p in posts)
    )
    stats = {
        'build_version': build_version,
        'image_policy': 'telegram_faithful_v3_proven_high_res',
        'public_pages_scanned': len(public['pages']),
        'public_posts_found': len(public['records']),
        'local_payload_posts': len(local_payloads),
        'registry_posts': len(registry),
        'publisher_proof_entries': len(publisher_proof),
        'merged_posts_with_images': len(posts),
        'total_slides': len(slides),
        'proven_high_res_posts': len(proven_posts),
        'telegram_preview_posts': sum(1 for p in posts if p['image_source_type'] == 'telegram_preview'),
        'telegram_full_stable_posts': sum(1 for p in posts if p['image_source_type'] == 'telegram_full_stable'),
        'source_full_posts_rendered': 0,  # invariant: source_full must never be rendered standalone
        'posts_hidden_no_telegram_images': posts_hidden_no_telegram_images,
        'posts_with_publisher_proof_but_count_mismatch': proven_but_count_mismatch,
        'posts_with_exactly_5_images': sum(1 for p in posts if len(p['image_urls']) == 5),
        'posts_with_non5_images': sum(1 for p in posts if len(p['image_urls']) != 5),
        'latest_message_id': max((p['message_id'] for p in posts), default=None),
        'earliest_message_id': min((p['message_id'] for p in posts), default=None),
        'grace_hours': GRACE_HOURS,
        'pending_grace_posts': pending_grace_posts,
        'excluded_nonpublic_registry_posts': sorted(mid for mid in registry if mid not in public_ids and mid not in pending_grace_posts),
        'public_pages': public['pages'],
    }
    posts_with_version = {'build_version': build_version, 'posts': posts}
    slides_with_version = {'build_version': build_version, 'slides': slides}
    (OUT_DIR / 'public_posts_raw.json').write_text(json.dumps(public, ensure_ascii=False, indent=2))
    (OUT_DIR / 'local_payload_posts.json').write_text(json.dumps(local_payloads, ensure_ascii=False, indent=2))
    (OUT_DIR / 'posts_catalog.json').write_text(json.dumps(posts, ensure_ascii=False, indent=2))
    (OUT_DIR / 'slides_catalog.json').write_text(json.dumps(slides, ensure_ascii=False, indent=2))
    (OUT_DIR / 'build_version.txt').write_text(build_version)

    # Compact, versioned slides.json consumed by the public slideshow frontend.
    # Fields are deliberately short to keep the payload small; the frontend reads
    # {id, mid, idx, title, arch, year, loc, url, post, src} per slide and uses
    # build_version for cache-busting image URLs.
    # English translations per message_id (title/arch/loc). Kept in a separate
    # file so they survive rebuilds; the frontend swaps them when EN is selected.
    translations = {}
    tpath = OUT_DIR / 'translations_en.json'
    if tpath.exists():
        try:
            raw = json.loads(tpath.read_text())
            if isinstance(raw, dict):
                translations = {str(k): v for k, v in raw.items() if isinstance(v, dict)}
        except Exception:
            translations = {}

    # ---- Фильтр качества витрины (CLAUDE.md, 2026-08-25) --------------------
    # Полные каталоги ops/site_data/* остаются верным зеркалом Telegram;
    # фильтр действует только на slides.json — то, что реально крутится на сайте.
    blocklist = load_slide_blocklist()
    dim_cache = load_dimension_cache()
    image_archive = load_image_archive()
    archived_fallbacks = 0
    removed_blocked = []
    removed_low_res = []
    removed_unmeasured = []
    upgraded_to_original = []
    probed_urls = set()

    if SITE_DIR.exists():
        compact_slides = []
        for s in slides:
            if (s['message_id'], s['index_in_post']) in blocklist:
                removed_blocked.append(s['slide_id'])
                continue
            render_url = s['image_url']
            probed_urls.add(render_url)
            wh = measure_image(render_url, dim_cache)
            if wh is not None and not meets_showcase_quality(*wh):
                # Основной URL мал — пробуем тот же кадр в полном разрешении.
                for cand in highres_candidates(render_url):
                    probed_urls.add(cand)
                    cwh = measure_image(cand, dim_cache)
                    if cwh and meets_showcase_quality(*cwh):
                        render_url, wh = cand, cwh
                        upgraded_to_original.append(s['slide_id'])
                        break
            if wh is None:
                removed_unmeasured.append(s['slide_id'])
                continue
            if not meets_showcase_quality(*wh):
                removed_low_res.append(s['slide_id'])
                continue
            mid = str(s['message_id'])
            tr = translations.get(mid, {})
            title = s.get('title', '')
            arch = s.get('architects', '')
            loc = s.get('location', '')
            entry = {
                'id': s['slide_id'],
                'mid': s['message_id'],
                'idx': s['index_in_post'],
                'title': title,
                'arch': arch,
                'year': s.get('year', ''),
                'loc': loc,
                # English fields fall back to the Russian value when no translation.
                'title_en': tr.get('title_en') or title,
                'arch_en': tr.get('arch_en', arch) if tr.get('arch_en') is not None else arch,
                'loc_en': tr.get('loc_en') or loc,
                'url': render_url,
                'post': s.get('telegram_post_url', ''),
                'src': s.get('image_source_type', ''),
            }
            fb = s.get('image_url_fallback') or ''
            if not fb and render_url != s['image_url']:
                # Апгрейд до /original/: страховка — прежний проверенный URL.
                fb = s['image_url']
            arch = image_archive.get(render_url)
            if isinstance(arch, dict) and arch.get('key'):
                # Приоритетный запасной — копия из нашего архива: то же
                # содержимое и разрешение, переживёт смерть первоисточника.
                fb = ARCHIVE_BASE_URL + arch['key']
                archived_fallbacks += 1
            if fb and fb != render_url:
                # Frontend retries with this URL if the primary fails.
                entry['url_fallback'] = fb
            compact_slides.append(entry)
        envelope = {
            'build_version': build_version,
            'image_policy': 'telegram_faithful_v4_quality_gate',
            'total': len(compact_slides),
            'slides': compact_slides,
        }
        (SITE_DIR / 'slides.json').write_text(
            json.dumps(envelope, ensure_ascii=False, separators=(',', ':'))
        )
        stats['showcase_slides'] = len(compact_slides)

    # Кэш размеров переписываем только URL-ами текущей сборки (основные +
    # проверенные original-кандидаты): протухшие превью-ссылки не копятся.
    current_urls = {s['image_url'] for s in slides} | probed_urls
    IMAGE_DIMENSIONS.write_text(json.dumps(
        {u: list(dim_cache[u]) for u in sorted(current_urls & set(dim_cache))},
        ensure_ascii=False, indent=0,
    ))

    stats['quality_gate'] = {
        'min_short_side': MIN_SHORT_SIDE,
        'archived_fallbacks': archived_fallbacks,
        'upgraded_to_original': len(upgraded_to_original),
        'upgraded_to_original_ids': upgraded_to_original,
        'removed_low_resolution': len(removed_low_res),
        'removed_low_resolution_ids': removed_low_res,
        'removed_blocklist_ids': removed_blocked,
        'removed_unmeasured_ids': removed_unmeasured,
    }
    (OUT_DIR / 'stats.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
