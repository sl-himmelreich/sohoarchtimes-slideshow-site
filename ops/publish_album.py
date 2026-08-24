#!/usr/bin/env python3
import json
import os
import sys
import time
import io
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps

MSK = ZoneInfo('Europe/Moscow')

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
if not TOKEN:
    raise SystemExit('TELEGRAM_BOT_TOKEN не задан: токен берётся только из переменной окружения, в этом публичном репо его хранить нельзя')
CHAT_ID = '-1003823260493'
SEND_URL = f'https://api.telegram.org/bot{TOKEN}/sendMediaGroup'
GET_FILE_URL = f'https://api.telegram.org/bot{TOKEN}/getFile'
FILE_BASE_URL = f'https://api.telegram.org/file/bot{TOKEN}'
REGISTRY_PATH = Path(__file__).resolve().parent / 'published_objects.json'
TMP_ROOT = Path('/tmp/sohoarchtimes_album_uploads')
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def load_registry():
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def save_registry(data):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _normalize_to_jpeg(content, out_path):
    img = Image.open(io.BytesIO(content))
    img = ImageOps.exif_transpose(img)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    elif img.mode == 'L':
        img = img.convert('RGB')
    max_side = max(img.size)
    if max_side > 2560:
        scale = 2560 / max_side
        new_size = (max(1, int(img.size[0] * scale)), max(1, int(img.size[1] * scale)))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    img.save(out_path, format='JPEG', quality=88, optimize=True)


def download_images(source_url, image_urls, slug):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': source_url,
    }
    folder = TMP_ROOT / slug
    folder.mkdir(parents=True, exist_ok=True)
    local_paths = []
    for idx, url in enumerate(image_urls, start=1):
        path = folder / f'{idx}.jpg'
        ok = False
        for attempt in range(3):
            try:
                r = session.get(url, headers=headers, timeout=90, allow_redirects=True)
                ctype = (r.headers.get('content-type', '') or '').lower()
                path_lower = urlparse(url).path.lower()
                looks_like_image = path_lower.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tif', '.tiff'))
                if r.status_code == 200 and len(r.content) > 20000 and (ctype.startswith('image/') or looks_like_image):
                    _normalize_to_jpeg(r.content, path)
                    local_paths.append(path)
                    ok = True
                    break
            except Exception:
                pass
            time.sleep(attempt + 1)
        if not ok:
            raise RuntimeError(f'Failed to download image {idx}: {url}')
    if len(local_paths) != 5:
        raise RuntimeError(f'Expected 5 local images, got {len(local_paths)}')
    return local_paths


def telegram_full_image_urls(messages):
    session = requests.Session()
    urls = []
    for msg in messages:
        photo_sizes = msg.get('photo') or []
        if not photo_sizes:
            continue
        best = max(photo_sizes, key=lambda x: (x.get('file_size', 0), x.get('width', 0) * x.get('height', 0)))
        file_id = best.get('file_id')
        if not file_id:
            continue
        resp = session.get(GET_FILE_URL, params={'file_id': file_id}, timeout=60)
        data = resp.json()
        file_path = ((data or {}).get('result') or {}).get('file_path')
        if file_path:
            urls.append(f'{FILE_BASE_URL}/{file_path}')
    return urls


def send_album(caption, local_paths):
    session = requests.Session()
    while True:
        media = []
        files = {}
        handles = []
        for i, path in enumerate(local_paths, start=1):
            entry = {'type': 'photo', 'media': f'attach://photo{i}'}
            if i == 1:
                entry['caption'] = caption
            media.append(entry)
            f = open(path, 'rb')
            handles.append(f)
            mime = 'image/jpeg'
            if path.suffix.lower() == '.webp':
                mime = 'image/webp'
            elif path.suffix.lower() == '.png':
                mime = 'image/png'
            files[f'photo{i}'] = (path.name, f, mime)
        try:
            resp = session.post(SEND_URL, data={'chat_id': CHAT_ID, 'media': json.dumps(media, ensure_ascii=False)}, files=files, timeout=180)
        finally:
            for f in handles:
                f.close()
        data = resp.json()
        if resp.status_code == 429 or data.get('parameters', {}).get('retry_after'):
            wait = int(data.get('parameters', {}).get('retry_after', 45)) + 2
            time.sleep(wait)
            continue
        if resp.status_code == 200 and data.get('ok') and len(data.get('result', [])) == 5:
            return data['result']
        raise RuntimeError(json.dumps(data, ensure_ascii=False))


def main():
    if len(sys.argv) != 2:
        print('Usage: publish_album.py /path/to/object.json', file=sys.stderr)
        sys.exit(2)
    obj = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    required = ['title', 'source_url', 'caption_ru', 'image_urls']
    for key in required:
        if key not in obj:
            raise RuntimeError(f'Missing required field: {key}')
    if len(obj['image_urls']) != 5:
        raise RuntimeError('Need exactly 5 image URLs')

    registry = load_registry()
    norm_title = obj['title'].strip().lower()
    source_url = obj['source_url'].strip()
    canonical_source = obj.get('canonical_source_url', '').strip()
    allow_duplicate = bool(obj.get('allow_duplicate'))
    duplicate_reason = obj.get('duplicate_reason', '').strip()
    if not allow_duplicate:
        for item in registry:
            if norm_title and item.get('title', '').strip().lower() == norm_title:
                raise RuntimeError('Duplicate title in registry')
            if source_url and item.get('source_url', '').strip() == source_url:
                raise RuntimeError('Duplicate source_url in registry')
            if canonical_source and item.get('canonical_source_url', '').strip() == canonical_source:
                raise RuntimeError('Duplicate canonical_source_url in registry')

    slug = obj.get('slug') or ''.join(ch if ch.isalnum() else '_' for ch in norm_title)[:80]
    local_paths = download_images(source_url, obj['image_urls'], slug)
    result = send_album(obj['caption_ru'], local_paths)
    first = result[0]
    msg_id = first.get('message_id')
    post_url = f'https://t.me/SohoArchTimes/{msg_id}'
    published_at = datetime.now(MSK)
    full_image_urls = telegram_full_image_urls(result)
    entry = {
        'title': obj['title'],
        'source_url': source_url,
        'canonical_source_url': canonical_source,
        'canonical_url': post_url,
        'date_published_to_telegram': published_at.strftime('%Y-%m-%d'),
        'datetime_published_to_telegram': published_at.isoformat(timespec='seconds'),
        'telegram_message_id': msg_id,
        'media_group_id': first.get('media_group_id'),
        'telegram_full_image_urls': full_image_urls,
    }
    if allow_duplicate:
        entry['allow_duplicate'] = True
        if duplicate_reason:
            entry['duplicate_reason'] = duplicate_reason
    registry.append(entry)
    save_registry(registry)
    print(json.dumps({'ok': True, 'post_url': post_url, 'message_id': msg_id, 'media_group_id': first.get('media_group_id'), 'telegram_full_image_urls': full_image_urls}, ensure_ascii=False))


if __name__ == '__main__':
    main()
