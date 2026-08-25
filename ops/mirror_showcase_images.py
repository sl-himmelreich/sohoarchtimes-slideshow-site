"""Зеркалирование кадров витрины в собственный архив (Yandex Object Storage).

Зачем: первоисточники (images.adsttc.com, parametric-architecture.com) могут
со временем удалить файлы или закрыть хотлинк. Архив в нашем бакете гарантирует,
что качество витрины не потеряется: сборщик ставит архивную копию в url_fallback
каждого кадра slides.json.

Запуск — только вручную по команде владельца (обычно после публикации нового
объекта): python ops/mirror_showcase_images.py

Ключи S3 в репозитории НЕ хранятся. Скрипт берёт их из:
  1) env YC_S3_ACCESS_KEY_ID + YC_S3_SECRET_ACCESS_KEY, либо
  2) JSON-файла по пути из env YC_S3_KEY_JSON вида
     {"accessKeyId": "...", "secret": "..."}
Как получить ключ заново — ops/SECRETS.md (IAM aws-compatibility accessKeys).

Схема архива: бакет soho-archtimes-site, ключ img/<sha256[:16]>.jpg
(content-addressed: имя = хэш содержимого, перезапись невозможна).
Манифест: ops/site_data/image_archive.json в репо (читает сборщик)
и копия img/manifest.json в бакете (на случай потери репо).
"""
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import boto3
import requests
from PIL import Image

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent
SLIDES = ROOT / 'slides.json'
ARCHIVE_MANIFEST = OPS / 'site_data' / 'image_archive.json'

BUCKET = 'soho-archtimes-site'
S3_ENDPOINT = 'https://storage.yandexcloud.net'
ARCHIVE_PREFIX = 'img/'

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})

MAX_BYTES = 64 * 1024 * 1024  # защита от аномально огромного файла


def s3_client():
    key_id = os.environ.get('YC_S3_ACCESS_KEY_ID')
    secret = os.environ.get('YC_S3_SECRET_ACCESS_KEY')
    if not (key_id and secret):
        key_file = os.environ.get('YC_S3_KEY_JSON')
        if not key_file:
            sys.exit('Нет ключей S3: задай YC_S3_ACCESS_KEY_ID/YC_S3_SECRET_ACCESS_KEY '
                     'или YC_S3_KEY_JSON (см. ops/SECRETS.md)')
        data = json.loads(Path(key_file).read_text())
        key_id, secret = data['accessKeyId'], data['secret']
    return boto3.client('s3', endpoint_url=S3_ENDPOINT,
                        aws_access_key_id=key_id, aws_secret_access_key=secret,
                        region_name='ru-central1')


def load_manifest():
    if ARCHIVE_MANIFEST.exists():
        try:
            raw = json.loads(ARCHIVE_MANIFEST.read_text())
            if isinstance(raw, dict):
                return raw
        except Exception:
            pass
    return {}


def download(url):
    r = SESSION.get(url, timeout=120, stream=True)
    r.raise_for_status()
    buf = io.BytesIO()
    for chunk in r.iter_content(1024 * 256):
        buf.write(chunk)
        if buf.tell() > MAX_BYTES:
            raise ValueError(f'файл больше {MAX_BYTES} байт: {url}')
    return buf.getvalue()


def main():
    slides = json.loads(SLIDES.read_text())['slides']
    manifest = load_manifest()
    s3 = s3_client()
    todo = [s for s in slides if s['url'] not in manifest]
    print(f'кадров на витрине: {len(slides)}; уже в архиве: {len(slides) - len(todo)}; '
          f'качаем: {len(todo)}', flush=True)
    errors = []
    for n, s in enumerate(todo, 1):
        url = s['url']
        try:
            body = download(url)
            im = Image.open(io.BytesIO(body))
            im.load()  # полная проверка целостности файла
            w, h = im.size
            sha = hashlib.sha256(body).hexdigest()
            ext = 'png' if (im.format or '').upper() == 'PNG' else \
                  'webp' if (im.format or '').upper() == 'WEBP' else 'jpg'
            ctype = {'jpg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}[ext]
            key = f'{ARCHIVE_PREFIX}{sha[:16]}.{ext}'
            s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType=ctype,
                          ACL='public-read',
                          CacheControl='public, max-age=31536000, immutable')
            manifest[url] = {'key': key, 'w': w, 'h': h,
                             'bytes': len(body), 'sha256': sha}
            print(f'[{n}/{len(todo)}] {s["id"]} -> {key} '
                  f'({w}x{h}, {len(body)/1e6:.1f} MB)', flush=True)
        except Exception as e:
            errors.append((s['id'], url, repr(e)))
            print(f'[{n}/{len(todo)}] {s["id"]} ОШИБКА: {e!r}', flush=True)
        if n % 10 == 0 or n == len(todo):
            ARCHIVE_MANIFEST.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True))
    ARCHIVE_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True))
    s3.put_object(Bucket=BUCKET, Key=f'{ARCHIVE_PREFIX}manifest.json',
                  Body=json.dumps(manifest, ensure_ascii=False).encode(),
                  ContentType='application/json; charset=utf-8', ACL='public-read',
                  CacheControl='no-cache')
    print(f'готово: в архиве {len(manifest)} кадров; ошибок: {len(errors)}', flush=True)
    for sid, url, err in errors:
        print('  не заархивирован:', sid, err, flush=True)


if __name__ == '__main__':
    main()
