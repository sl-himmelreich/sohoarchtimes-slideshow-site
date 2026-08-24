#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SOHO Calendar Assistant — автономный ежедневный запуск (GitHub Actions).

Полный конвейер без участия Claude-сессий:
  Telegram (getUpdates) -> разбор текста (Claude API, при сбое/отсутствии
  ключа — встроенный ru_parser) -> дубликаты -> Google Calendar (сервисный
  аккаунт) -> подтверждения ✅/⚠️ владельцу -> подтверждение offset.

Дисциплина ошибок: offset подтверждается СТРОГО в конце и только если весь
запуск прошёл без единой ошибки. Любое исключение валит процесс ненулевым
кодом, offset не подтверждается, сообщения приходят повторно в следующий
запуск (дубликаты в календаре отсекает has_duplicate).

Пустой запуск — полная тишина: никаких сообщений в Telegram.
"""

import sys
from datetime import datetime

import tg_pipeline
from tg_pipeline import WEEKDAYS_RU


def build_confirmations(created, unrecognized_count):
    """Тексты подтверждений по форматам PARSING_RULES.md."""
    out = []
    if len(created) == 1:
        ev = created[0]
        d = datetime.fromisoformat(ev["date"])
        out.append(f"✅ Добавлено: {ev['summary']}, {d.strftime('%d.%m')}, {ev['time']}")
    elif len(created) > 1:
        lines = [f"✅ Добавлено {len(created)} событий:"]
        for ev in created:
            d = datetime.fromisoformat(ev["date"])
            lines.append(f"• {d.strftime('%d.%m')} ({WEEKDAYS_RU[d.weekday()]}) "
                         f"{ev['time']} — {ev['summary']}")
        out.append("\n".join(lines))
    for _ in range(unrecognized_count):
        out.append("⚠️ Не удалось распознать событие. Пример формата: "
                   "«3 апреля 14:00 30 мин встреча с Петровым»")
    return out


def main():
    data = tg_pipeline.fetch_data()
    print(f"updates_total={data['updates_total']}, "
          f"messages={len(data['messages'])}, "
          f"webhook_deleted={data['webhook_deleted']}")

    if not data["messages"]:
        if data["updates_total"] > 0:
            tg_pipeline.confirm_offset(data["max_update_id"] + 1)
            print("пустой запуск: offset подтверждён, тишина")
        else:
            print("пустой запуск: очередь пуста, тишина")
        print("ASSISTANT_RUN_COMPLETE")
        return

    from claude_parser import parse_with_claude
    parsed = parse_with_claude(data["messages"])
    if parsed is None:
        from ru_parser import parse_messages
        parsed = parse_messages(data["messages"])
        print("разбор: встроенный ru_parser")
    else:
        print("разбор: Claude API")

    from gcal import GCal
    cal = GCal()

    created, skipped = [], []
    for ev in parsed["events"]:
        if cal.has_duplicate(ev["date"], ev["summary"]):
            skipped.append(ev)
            print(f"дубль пропущен: {ev['date']} «{ev['summary']}»")
            continue
        cal.insert(ev)
        created.append(ev)
        print(f"создано: {ev['date']} {ev['time']} «{ev['summary']}»"
              + (f" [{ev['rrule']}]" if ev.get("rrule") else ""))

    for text in build_confirmations(created, len(parsed["unrecognized_message_ids"])):
        tg_pipeline.send_text(text)
        print("отправлено подтверждение")

    tg_pipeline.confirm_offset(data["max_update_id"] + 1)
    print(f"offset подтверждён: {data['max_update_id'] + 1}")
    print(f"итог: создано {len(created)}, дублей {len(skipped)}, "
          f"нераспознано {len(parsed['unrecognized_message_ids'])}")
    print("ASSISTANT_RUN_COMPLETE")


if __name__ == "__main__":
    main()
