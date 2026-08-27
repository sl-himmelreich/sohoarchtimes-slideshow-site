#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOHO Calendar Assistant — механика Telegram Bot API (fetch / send / confirm).

Используется двояко:
  * как библиотека из run_assistant.py (GitHub Actions, ежедневно 21:00 МСК);
  * как CLI из Claude-сессии временного моста (см. ROUTINE.md).

Порядок запуска:
  1. fetch   — getWebhookInfo (+ deleteWebhook при непустом url), затем
               getUpdates БЕЗ offset (timeout=0, limit=100) → все
               неподтверждённые сообщения личного чата (последние редакции).
               Исполняются ТОЛЬКО сообщения владельца (OWNER_USER_ID,
               @Sl_Himmelreich): чужой автор, отправка от имени канала и
               пересланный чужой текст отбрасываются до разбора. Это важно
               с 27.08.2026: у бота выключен режим приватности, и в очередь
               попадают реплики рабочей группы «ГРАНАРД — Новоясеневский».
  2. send    — sendMessage подтверждения владельцу (текст через --text или stdin).
  3. confirm — getUpdates?offset=<max_update_id+1>&limit=1 — подтверждение приёма.
               СТРОГО в конце и ТОЛЬКО если весь запуск прошёл без единой
               ошибки; иначе offset не подтверждать — сообщения придут повторно.

Токен — только из env TELEGRAM_BOT_TOKEN, в файлы и логи не попадает.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

PERSONAL_CHAT_ID = 1294602429  # единственный обрабатываемый чат (личный чат владельца)
OWNER_USER_ID = 1294602429  # @Sl_Himmelreich (+7 909 907-33-00) — единственный автор команд
ACCEPT_FORWARDS = False  # True — исполнять и пересланный владельцем чужой текст
MSK = timezone(timedelta(hours=3))
WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def api(method, **params):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN не задан в окружении")
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/{method}", data=params, timeout=30
    )
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(
            f"{method} failed: {data.get('error_code')} {data.get('description')}"
        )
    return data["result"]


def fetch_data():
    """Неподтверждённые сообщения личного чата; см. модульный докстринг."""
    webhook_deleted = False
    if api("getWebhookInfo").get("url"):
        api("deleteWebhook", drop_pending_updates="false")
        webhook_deleted = True

    updates = api("getUpdates", timeout=0, limit=100)
    max_update_id = max((u["update_id"] for u in updates), default=None)

    # Для одного message_id берётся последняя редакция: edited_message с
    # максимальным edit_date перекрывает оригинал, черновики не обрабатываются.
    by_mid = {}
    for u in updates:
        msg = u.get("message") or u.get("edited_message")
        if not msg:
            continue  # channel_post и прочие типы апдейтов — игнор
        if msg.get("chat", {}).get("id") != PERSONAL_CHAT_ID:
            continue  # любые другие чаты и каналы — игнор
        if (msg.get("from") or {}).get("id") != OWNER_USER_ID:
            continue  # команды исполняются ТОЛЬКО от владельца; сообщение от имени
            # канала/группы приходит без from и отсекается здесь же
        if not ACCEPT_FORWARDS and (msg.get("forward_origin") or msg.get("forward_from")
                                    or msg.get("forward_sender_name")
                                    or msg.get("forward_from_chat")):
            continue  # пересланный чужой текст командой владельца не считается
        text = msg.get("text")
        if not text or text.startswith("/"):
            continue  # нетекстовое и команды — игнор
        rev = msg.get("edit_date", 0)
        cur = by_mid.get(msg["message_id"])
        if cur is None or rev >= cur[0]:
            by_mid[msg["message_id"]] = (rev, msg)

    messages = []
    for mid in sorted(by_mid):
        msg = by_mid[mid][1]
        dt = datetime.fromtimestamp(msg["date"], MSK)
        messages.append({
            "message_id": mid,
            "date_msk": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "weekday_msk": WEEKDAYS_RU[dt.weekday()],
            "edited": bool(msg.get("edit_date")),
            "text": msg["text"],
        })

    return {
        "webhook_deleted": webhook_deleted,
        "updates_total": len(updates),
        "max_update_id": max_update_id,
        "messages": messages,
    }


def send_text(text):
    if not text.strip():
        raise ValueError("пустой текст подтверждения")
    api("sendMessage", chat_id=PERSONAL_CHAT_ID, text=text)


def confirm_offset(offset):
    api("getUpdates", offset=offset, limit=1, timeout=0)


def cmd_fetch(_args):
    json.dump(fetch_data(), sys.stdout, ensure_ascii=False, indent=2)
    print()


def cmd_send(args):
    send_text(args.text if args.text is not None else sys.stdin.read())
    print("sent")


def cmd_confirm(args):
    confirm_offset(args.offset)
    print(f"confirmed: offset={args.offset}")


def main():
    p = argparse.ArgumentParser(description="Механика Telegram для SOHO Calendar Assistant")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch").set_defaults(func=cmd_fetch)
    ps = sub.add_parser("send")
    ps.add_argument("--text", help="текст сообщения; без флага читается из stdin")
    ps.set_defaults(func=cmd_send)
    pc = sub.add_parser("confirm")
    pc.add_argument("--offset", type=int, required=True, help="max_update_id + 1")
    pc.set_defaults(func=cmd_confirm)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
