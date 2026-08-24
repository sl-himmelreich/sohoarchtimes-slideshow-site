#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Google Calendar через сервисный аккаунт (headless, для GitHub Actions).

Секреты (env):
  GOOGLE_SA_KEY     — полное содержимое JSON-ключа сервисного аккаунта;
  GCAL_CALENDAR_ID  — id календаря владельца (его gmail-адрес); календарь
                      должен быть расшарен на email сервисного аккаунта с
                      правом «Внесение изменений в мероприятия».
Scope минимальный: calendar.events.
"""

import difflib
import json
import os
import re
import urllib.parse
from datetime import datetime, timedelta

import requests

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
API = "https://www.googleapis.com/calendar/v3"
TZ = "Europe/Moscow"
SIMILARITY = 0.85


def _norm(s):
    s = (s or "").lower().replace("ё", "е")
    return re.sub(r"\s+", " ", re.sub(r"[^\wа-я ]", " ", s)).strip()


def similar(a, b):
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return False
    return a == b or difflib.SequenceMatcher(None, a, b).ratio() >= SIMILARITY


class GCal:
    def __init__(self):
        raw = os.environ.get("GOOGLE_SA_KEY")
        self.calendar_id = os.environ.get("GCAL_CALENDAR_ID")
        if not raw:
            raise RuntimeError("GOOGLE_SA_KEY не задан")
        if not self.calendar_id:
            raise RuntimeError("GCAL_CALENDAR_ID не задан")
        from google.oauth2 import service_account
        import google.auth.transport.requests
        creds = service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=SCOPES)
        creds.refresh(google.auth.transport.requests.Request())
        self._headers = {"Authorization": f"Bearer {creds.token}"}
        self._base = f"{API}/calendars/{urllib.parse.quote(self.calendar_id)}/events"

    def summaries_on_date(self, date_iso):
        """Названия событий календаря в дату date_iso (МСК)."""
        day = datetime.fromisoformat(date_iso)
        params = {
            "timeMin": day.strftime("%Y-%m-%dT00:00:00+03:00"),
            "timeMax": (day + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+03:00"),
            "singleEvents": "true",
            "maxResults": 250,
        }
        r = requests.get(self._base, params=params, headers=self._headers, timeout=30)
        r.raise_for_status()
        return [item.get("summary", "") for item in r.json().get("items", [])]

    def has_duplicate(self, date_iso, summary):
        return any(similar(summary, s) for s in self.summaries_on_date(date_iso))

    def insert(self, ev):
        """ev — объект контракта парсеров; возвращает htmlLink."""
        start = f"{ev['date']}T{ev['time']}:00"
        if ev.get("end_time"):
            end = f"{ev.get('end_date', ev['date'])}T{ev['end_time']}:00"
        else:
            dt = datetime.fromisoformat(start) + timedelta(
                minutes=int(ev.get("duration_min", 60)))
            end = dt.strftime("%Y-%m-%dT%H:%M:%S")
        body = {
            "summary": ev["summary"],
            "description": ev.get("description", "Из Telegram"),
            "start": {"dateTime": start, "timeZone": TZ},
            "end": {"dateTime": end, "timeZone": TZ},
        }
        if ev.get("rrule"):
            body["recurrence"] = [ev["rrule"]]
        r = requests.post(self._base, json=body, headers=self._headers, timeout=30)
        r.raise_for_status()
        return r.json().get("htmlLink", "")
