#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import publish_album as base

def main():
    if len(sys.argv) != 2:
        print('Usage: publish_album_allow_duplicates.py /path/to/object.json', file=sys.stderr)
        sys.exit(2)
    obj = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    required = ['title', 'source_url', 'caption_ru', 'image_urls']
    for key in required:
        if key not in obj:
            raise RuntimeError(f'Missing required field: {key}')
    if len(obj['image_urls']) != 5:
        raise RuntimeError('Need exactly 5 image URLs')
    slug = obj.get('slug') or ''.join(ch if ch.isalnum() else '_' for ch in obj['title'].strip().lower())[:80]
    local_paths = base.download_images(obj['source_url'], obj['image_urls'], slug)
    result = base.send_album(obj['caption_ru'], local_paths)
    first = result[0]
    msg_id = first.get('message_id')
    post_url = f'https://t.me/SohoArchTimes/{msg_id}'
    registry = base.load_registry()
    registry.append({
        'title': obj['title'],
        'source_url': obj['source_url'].strip(),
        'canonical_source_url': obj.get('canonical_source_url', '').strip(),
        'canonical_url': post_url,
        'date_published_to_telegram': base.time.strftime('%Y-%m-%d'),
        'telegram_message_id': msg_id,
        'media_group_id': first.get('media_group_id'),
        'manual_exception_duplicate_allowed': True
    })
    base.save_registry(registry)
    print(json.dumps({'ok': True, 'post_url': post_url, 'message_id': msg_id, 'media_group_id': first.get('media_group_id')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
