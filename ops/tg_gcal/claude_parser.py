#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Основной разбор сообщений через Claude API (модель claude-opus-5).

Системный промпт — дословно ops/tg_gcal/PARSING_RULES.md + контракт JSON.
Чистый вызов «текст -> JSON», без инструментов. Выполняется не чаще раза в
сутки и только при наличии новых сообщений (экономия — требование владельца).

Возвращает dict контракта или None — тогда вызывающий код обязан перейти на
аварийный fallback ru_parser (регулярки), как требуют правила.
"""

import json
import os
import re
from pathlib import Path

MODEL = "claude-opus-5"

CONTRACT = """
---
Задача: разобрать входные сообщения Telegram в события календаря СТРОГО по
правилам выше. Вход — JSON-список сообщений с полями message_id, date_msk
(«YYYY-MM-DD HH:MM:SS», МСК — база всех относительных дат этого сообщения),
weekday_msk и text.

Ответ — ТОЛЬКО валидный JSON без пояснений и без markdown-ограждений:
{
  "events": [
    {
      "summary": "название по правилам",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "duration_min": 60,                  // ИЛИ end_date/end_time вместо длительности
      "end_date": "YYYY-MM-DD",            // опционально (диапазоны, отъезд/приезд)
      "end_time": "HH:MM",                 // опционально
      "rrule": "RRULE:FREQ=...",           // опционально, для повторов
      "description": "Из Telegram...",     // всегда начинается с «Из Telegram»;
                                           // сюда же строки про неуказанное время и «Контекст: «...»»
      "source_message_id": 123
    }
  ],
  "unrecognized_message_ids": [124]        // сообщения-«не события» (ответ ⚠️)
}

Сообщение, дающее несколько дел, даёт несколько объектов events.
Никакого текста вне JSON-объекта.
"""

SYSTEM = Path(__file__).with_name("PARSING_RULES.md").read_text(encoding="utf-8") + CONTRACT


def parse_with_claude(messages):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("claude_parser: ANTHROPIC_API_KEY не задан — работает встроенный парсер")
        return None
    try:
        import anthropic
        client = anthropic.Anthropic()
        payload = json.dumps(messages, ensure_ascii=False, indent=1)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=[{"role": "user", "content": payload}],
        )
        if resp.stop_reason == "refusal":
            print("claude_parser: refusal — переход на встроенный парсер")
            return None
        text = "".join(b.text for b in resp.content if b.type == "text")
        m = re.search(r"\{.*\}", text, re.S)
        data = json.loads(m.group(0))
        assert isinstance(data.get("events"), list)
        assert isinstance(data.get("unrecognized_message_ids"), list)
        for ev in data["events"]:
            assert ev.get("summary") and ev.get("date") and ev.get("time")
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", ev["date"])
            assert re.fullmatch(r"\d{2}:\d{2}", ev["time"])
            if not ev.get("description", "").startswith("Из Telegram"):
                ev["description"] = ("Из Telegram\n" + ev.get("description", "")).strip()
        return data
    except Exception as e:  # любой сбой API/формата -> аварийный fallback
        print(f"claude_parser: fallback из-за {type(e).__name__}: {e}")
        return None
