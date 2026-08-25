#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Разбор сообщений в события через LLM (DeepSeek — основной, Claude — запасной).

Системный промпт — дословно ops/tg_gcal/PARSING_RULES.md + строгий JSON-контракт.
Чистый вызов «текст -> JSON», без инструментов. Вызывается не чаще раза в сутки и
только при наличии новых сообщений (экономия — требование владельца).

Ключи только из окружения (в файлы/логи/репозиторий не попадают):
  DEEPSEEK_API_KEY   — приоритетный разбор через DeepSeek (api.deepseek.com,
                       OpenAI-совместимый; модель DEEPSEEK_MODEL, по умолч.
                       deepseek-chat) — десятки раз дешевле Claude.
  ANTHROPIC_API_KEY  — запасной разбор через Claude (SDK anthropic, опционально).

Возвращает dict контракта или None — тогда вызывающий код обязан перейти на
встроенный парсер ru_parser (регулярки), как требуют правила.
"""

import json
import os
import re
from pathlib import Path

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


def _extract_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("в ответе нет JSON-объекта")
    return json.loads(m.group(0))


def _validate(data):
    assert isinstance(data.get("events"), list)
    assert isinstance(data.get("unrecognized_message_ids"), list)
    for ev in data["events"]:
        assert ev.get("summary") and ev.get("date") and ev.get("time")
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", ev["date"])
        assert re.fullmatch(r"\d{2}:\d{2}", ev["time"])
        if not str(ev.get("description", "")).startswith("Из Telegram"):
            ev["description"] = ("Из Telegram\n" + str(ev.get("description", ""))).strip()
    return data


def _deepseek(messages):
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    import requests
    payload = json.dumps(messages, ensure_ascii=False, indent=1)
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": payload},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    return _validate(_extract_json(text))


def _claude(messages):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    import anthropic  # опциональная зависимость; ставится только если нужен Claude
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-opus-5"),
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": json.dumps(messages, ensure_ascii=False, indent=1)}],
    )
    if resp.stop_reason == "refusal":
        return None
    text = "".join(b.text for b in resp.content if b.type == "text")
    return _validate(_extract_json(text))


def parse_with_llm(messages):
    """DeepSeek -> Claude; None, если ни один провайдер не сработал."""
    for name, fn in (("DeepSeek", _deepseek), ("Claude", _claude)):
        try:
            out = fn(messages)
        except Exception as e:  # сбой провайдера -> следующий, затем встроенный парсер
            print(f"llm_parser: {name} недоступен ({type(e).__name__}: {e})")
            continue
        if out is not None:
            print(f"разбор: {name}")
            return out
    return None
