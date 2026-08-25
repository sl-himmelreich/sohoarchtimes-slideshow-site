#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Детерминированный разбор русских сообщений в события календаря.

Аварийный fallback по ops/tg_gcal/PARSING_RULES.md: используется, когда
основной разбор через Claude API недоступен (нет ANTHROPIC_API_KEY) или
упал. Всё, что не удаётся разобрать надёжно, помечается нераспознанным
(⚠️) — это штатное поведение, а не ошибка.

Вход:  список сообщений [{"message_id", "date_msk" ("YYYY-MM-DD HH:MM:SS"),
       "text"}] в хронологическом порядке.
Выход: {"events": [...], "unrecognized_message_ids": [...]} — контракт общий
       с claude_parser.py. Все даты/времена наивные, в МСК.
"""

import re
from datetime import date, datetime, timedelta

DEFAULT_DURATION_MIN = 60
DEFAULT_TIME = (9, 0)
FOLLOWUP_WINDOW_MIN = 30

MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
              "августа", "сентября", "октября", "ноября", "декабря"]
MONTHS_PREP = ["январе", "феврале", "марте", "апреле", "мае", "июне", "июле",
               "августе", "сентябре", "октябре", "ноябре", "декабре"]
WD_STEMS = [r"понедельник(?:а|у)?", r"вторник(?:а|у)?", r"сред(?:а|у|е|ы)",
            r"четверг(?:а|у)?", r"пятниц(?:а|у|е|ы)", r"суббот(?:а|у|е|ы)",
            r"воскресень(?:е|я|ю)"]
WD_PLURAL = ["понедельникам", "вторникам", "средам", "четвергам", "пятницам",
             "субботам", "воскресеньям"]
WD_RE = "|".join(f"(?P<wd{i}>{s})" for i, s in enumerate(WD_STEMS))
BYDAY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

WORD_UNITS = {"ноль": 0, "один": 1, "одну": 1, "одна": 1, "два": 2, "две": 2,
              "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
              "восемь": 8, "девять": 9, "десять": 10, "одиннадцать": 11,
              "двенадцать": 12, "тринадцать": 13, "четырнадцать": 14,
              "пятнадцать": 15, "шестнадцать": 16, "семнадцать": 17,
              "восемнадцать": 18, "девятнадцать": 19}
WORD_TENS = {"двадцать": 20, "тридцать": 30, "сорок": 40, "пятьдесят": 50}

COMMAND_PREFIX = re.compile(
    r"^\s*(?:внеси(?:те)?|вынеси(?:те)?|неси|занеси|запиши(?:те)?|поставь(?:те)?|"
    r"добавь(?:те)?|создай(?:те)?|внести|добавить|записать|поставить|создать)"
    r"\b(?:\s+(?:в|на)\s+календарь)?(?:\s+(?:мне|пожалуйста))*"
    r"(?:\s+(?:в|на|к)\b)?\s*[:,-]?\s*",
    re.IGNORECASE)


class _Text:
    """Строка с масками: совпадения гасятся пробелами и там, и в оригинале."""

    def __init__(self, text):
        self.orig = list(text)
        self.norm = list(text.lower().replace("ё", "е"))

    def s(self):
        return "".join(self.norm)

    def blank(self, start, end):
        for i in range(start, end):
            self.norm[i] = " "
            self.orig[i] = " "

    def take(self, pattern, flags=0):
        m = re.search(pattern, self.s(), flags)
        if m:
            self.blank(m.start(), m.end())
        return m

    def remainder(self):
        return re.sub(r"\s+", " ", "".join(self.orig)).strip(" ,.;:-—–")


def _wd_index(m):
    for i in range(7):
        if m.groupdict().get(f"wd{i}"):
            return i
    return None


def _word_number(tokens):
    """Число из 1–2 словесных токенов; -> (значение, съедено токенов) или None."""
    if not tokens:
        return None
    t0 = tokens[0]
    if t0 in WORD_TENS:
        if len(tokens) > 1 and tokens[1] in WORD_UNITS and WORD_UNITS[tokens[1]] < 10:
            return WORD_TENS[t0] + WORD_UNITS[tokens[1]], 2
        return WORD_TENS[t0], 1
    if t0 in WORD_UNITS:
        return WORD_UNITS[t0], 1
    return None


def _nearest_future_date(day, month, base, year=None):
    if year:
        return date(year, day=day, month=month)
    d = date(base.year, month, day)
    if d < base.date():
        d = date(base.year + 1, month, day)
    return d


def _nearest_dom(day, base):
    """Ближайшее N-е число (сегодняшнее прошло -> следующий месяц)."""
    d = base.date()
    y, m = d.year, d.month
    for _ in range(24):
        try:
            cand = date(y, m, day)
        except ValueError:
            cand = None
        if cand and cand > d:
            return cand
        m += 1
        if m == 13:
            y, m = y + 1, 1
    raise ValueError("нет подходящей даты")


def _month_end_until(month, base):
    """UNTIL (UTC) — конец ближайшего будущего/текущего месяца month."""
    y = base.year if month >= base.month else base.year + 1
    nm_y, nm_m = (y, month + 1) if month < 12 else (y + 1, 1)
    end_msk = datetime(nm_y, nm_m, 1) - timedelta(seconds=1)
    return (end_msk - timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")


def _extract_rrule(t, base):
    """-> (rrule|None, byday_indices|None, monthly_day|None)."""
    until = ""
    mm = re.search(r"\bв\s+(" + "|".join(MONTHS_PREP) + r")\b", t.s())
    scope_month = MONTHS_PREP.index(mm.group(1)) + 1 if mm else None

    m = t.take(r"\b(?:ежедневно|каждый\s+день)\b")
    if m:
        if scope_month:
            until = ";UNTIL=" + _month_end_until(scope_month, base)
            t.take(r"\bв\s+(" + "|".join(MONTHS_PREP) + r")\b")
        return "RRULE:FREQ=DAILY" + until, None, None

    m = t.take(r"\bпо\s+будням\b")
    if m:
        days = "MO,TU,WE,TH,FR"
        if scope_month:
            until = ";UNTIL=" + _month_end_until(scope_month, base)
            t.take(r"\bв\s+(" + "|".join(MONTHS_PREP) + r")\b")
        return f"RRULE:FREQ=WEEKLY;BYDAY={days}" + until, [0, 1, 2, 3, 4], None

    m = t.take(r"\bкажд(?:ый|ую|ое)\s+(?:" + WD_RE + r")\b")
    if not m:
        m = t.take(r"\bпо\s+(?:" + "|".join(
            f"(?P<wd{i}>{w})" for i, w in enumerate(WD_PLURAL)) + r")\b")
    if m:
        i = _wd_index(m)
        if scope_month:
            until = ";UNTIL=" + _month_end_until(scope_month, base)
            t.take(r"\bв\s+(" + "|".join(MONTHS_PREP) + r")\b")
        return f"RRULE:FREQ=WEEKLY;BYDAY={BYDAY[i]}" + until, [i], None

    m = t.take(r"\b(\d{1,2})\s+числа\s+каждого\s+месяца\b")
    if m:
        day = int(m.group(1))
        return f"RRULE:FREQ=MONTHLY;BYMONTHDAY={day}" + until, None, day
    return None, None, None


def _extract_date(t, base):
    """-> (date|None, kind, context_note). kind: explicit|weekday|None."""
    note = ""
    m = t.take(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1))), "explicit", note

    m = t.take(r"\b(\d{1,2})\s+(" + "|".join(MONTHS_GEN) + r")(?:\s+(\d{4}))?\b")
    if m:
        month = MONTHS_GEN.index(m.group(2)) + 1
        year = int(m.group(3)) if m.group(3) else None
        return _nearest_future_date(int(m.group(1)), month, base, year), "explicit", note

    m = t.take(r"\b(\d{1,2})\s+числа\b(?!\s+каждого)")
    if m:
        return _nearest_dom(int(m.group(1)), base), "explicit", note

    rel = None
    m = t.take(r"\bпослезавтра\b")
    if m:
        rel = base.date() + timedelta(days=2)
    else:
        m = t.take(r"\bзавтра\b")
        if m:
            rel = base.date() + timedelta(days=1)
        else:
            m = t.take(r"\bсегодня\b")
            if m:
                rel = base.date()
            else:
                m = t.take(r"\bчерез\s+(\d{1,3}|"
                           + "|".join(list(WORD_TENS) + list(WORD_UNITS))
                           + r")\s+(?:день|дня|дней)\b")
                if m:
                    tok = m.group(1)
                    n = int(tok) if tok.isdigit() else (
                        WORD_TENS.get(tok) or WORD_UNITS.get(tok))
                    rel = base.date() + timedelta(days=n)

    wd_date = None
    m = t.take(r"(?:\b(?:в|во|на)\s+)?\b(?:" + WD_RE + r")\s+на\s+следующей\s+неделе\b")
    if not m:
        m = t.take(r"\bследующ(?:ий|ую|ее|ей)\s+(?:в\s+|во\s+)?(?:" + WD_RE + r")\b")
    if m:
        i = _wd_index(m)
        wd_date = base.date() + timedelta(days=(7 - base.weekday()) + i)
    else:
        m = t.take(r"(?:\b(?:в|во|на)\s+)?\b(?:" + WD_RE + r")\s+на\s+этой\s+неделе\b")
        if m:
            i = _wd_index(m)
            wd_date = base.date() + timedelta(days=i - base.weekday())
            if wd_date < base.date():
                wd_date += timedelta(days=7)
        else:
            m = t.take(r"(?:\b(?:в|во|на)\s+)\b(?:" + WD_RE + r")\b")
            if m:
                i = _wd_index(m)
                delta = (i - base.weekday()) % 7
                wd_date = base.date() + timedelta(days=delta)
                # delta 0 = сегодня; уточняется позже по времени (weekday-kind)

    if wd_date and rel is not None:
        # лишняя оговорка: дата из дня недели, оговорку — в description
        word = {1: "завтра", 2: "послезавтра", 0: "сегодня"}.get(
            (rel - base.date()).days, "оговорка о дате")
        return wd_date, "weekday", f"Контекст: «{word}»."
    if wd_date:
        return wd_date, "weekday", note
    if rel is not None:
        return rel, "explicit", note

    m = t.take(r"\b(\d{1,2})\.(0[1-9]|1[0-2])\b(?!\.)")
    if m and int(m.group(1)) <= 31:
        # DD.MM с ведущим нулём месяца — дата «как написано», без года
        return _nearest_future_date(int(m.group(1)), int(m.group(2)), base), "explicit", note
    return None, None, note


def _hours_shift(h, suffix):
    if suffix == "утра":
        return h
    if suffix == "дня":
        return h + 12 if h < 12 else h
    if suffix == "вечера":
        return h + 12 if h < 12 else h
    if suffix == "ночи":
        return 0 if h == 12 else h
    return h


def _extract_range(t):
    m = t.take(r"\bс\s+(\d{1,2})(?::(\d{2}))?\s+до\s+(\d{1,2})(?::(\d{2}))?\b")
    if m:
        return ((int(m.group(1)), int(m.group(2) or 0)),
                (int(m.group(3)), int(m.group(4) or 0)))
    m = t.take(r"\b(\d{1,2}):(\d{2})\s*[-–—]\s*(\d{1,2}):(\d{2})\b")
    if m:
        return ((int(m.group(1)), int(m.group(2))),
                (int(m.group(3)), int(m.group(4))))
    return None


def _extract_times(t):
    """Все явные времена в порядке появления: [(h, m, pos)]."""
    out = []
    for pat in (r"\b(\d{1,2}):(\d{2})\b", r"\b(\d{1,2})-([0-5]\d)\b",
                r"\b(\d{1,2})\.([0-5]\d)\b"):
        while True:
            m = t.take(pat)
            if not m:
                break
            h, mi = int(m.group(1)), int(m.group(2))
            if h <= 23:
                out.append((h, mi, m.start()))
    m = t.take(r"\b(?:в\s+)?(\d{1,2})\s+час(?:а|ов)?(?:\s+(\d{1,2})\s+минут[уы]?)?\b")
    if m:
        out.append((int(m.group(1)), int(m.group(2) or 0), m.start()))
    while True:
        m = t.take(r"\b(?:в\s+)?(\d{1,2})\s+(утра|дня|вечера|ночи)\b")
        if not m:
            break
        out.append((_hours_shift(int(m.group(1)), m.group(2)), 0, m.start()))
    # словесные числительные: «в девять вечера», «двадцать один тридцать»
    m = t.take(r"\b(?:в\s+)?(" + "|".join(list(WORD_TENS) + list(WORD_UNITS))
               + r")(?:\s+(" + "|".join(list(WORD_TENS) + list(WORD_UNITS))
               + r"))?\s+(утра|дня|вечера|ночи)\b")
    if m:
        toks = [x for x in (m.group(1), m.group(2)) if x]
        val = _word_number(toks)
        if val and val[0] <= 12:
            out.append((_hours_shift(val[0], m.group(3)), 0, m.start()))
    m = t.take(r"\b(" + "|".join(list(WORD_TENS) + list(WORD_UNITS)) + r")"
               r"(?:\s+(" + "|".join(u for u in WORD_UNITS if WORD_UNITS[u] < 10) + r"))?"
               r"\s+(" + "|".join(list(WORD_TENS) + list(WORD_UNITS)) + r")"
               r"(?:\s+(" + "|".join(u for u in WORD_UNITS if WORD_UNITS[u] < 10) + r"))?\b")
    if m:
        toks = [x for x in m.groups() if x]
        h = _word_number(toks)
        if h:
            rest = toks[h[1]:]
            mi = _word_number(rest)
            if mi and h[0] <= 23 and mi[0] <= 59 and not rest[mi[1]:]:
                out.append((h[0], mi[0], m.start()))
    out.sort(key=lambda x: x[2])
    return [(h, mi) for h, mi, _ in out]


def _extract_daypart(t):
    for pat, hm in ((r"\bутром\b", (9, 0)), (r"\bднем\b", (13, 0)),
                    (r"\bвечером\b", (19, 0)), (r"\bночью\b", (22, 0))):
        if t.take(pat):
            return hm
    return None


def _extract_duration(t):
    m = t.take(r"\b(?:на\s+)?полтора\s+часа\b")
    if m:
        return 90
    m = t.take(r"\b(?:на\s+)?полчаса\b")
    if m:
        return 30
    m = t.take(r"\b(\d{1,3})\s*(?:мин(?:ут[уы]?)?\.?)\b")
    if m:
        return int(m.group(1))
    m = t.take(r"\b(?:на\s+)?(\d{1,2})\s*час(?:а|ов)?\b")
    if m:
        return int(m.group(1)) * 60
    m = t.take(r"\bна\s+час\b")
    if m:
        return 60
    return None


def _title(t):
    raw = t.remainder()
    raw = COMMAND_PREFIX.sub("", raw)
    raw = re.sub(r"\s+", " ", raw).strip(" ,.;:-—–")
    if not raw:
        return "Событие"
    return raw[0].upper() + raw[1:]


def _rrule_start(byday, monthly_day, hm, base):
    if monthly_day:
        return _nearest_dom(monthly_day, base)
    if byday is not None:
        best = None
        for i in byday:
            delta = (i - base.weekday()) % 7
            cand = base.date() + timedelta(days=delta)
            if delta == 0 and (hm[0], hm[1]) <= (base.hour, base.minute):
                cand += timedelta(days=7)
            if best is None or cand < best:
                best = cand
        return best
    # DAILY: сегодня, если время впереди, иначе завтра
    d = base.date()
    if (hm[0], hm[1]) <= (base.hour, base.minute):
        d += timedelta(days=1)
    return d


def _parse_segment(text, base, inherited_date):
    t = _Text(text)
    rrule, byday, monthly_day = _extract_rrule(t, base)
    d, kind, note = _extract_date(t, base)
    rng = _extract_range(t)
    times = _extract_times(t)
    daypart = _extract_daypart(t)
    duration = _extract_duration(t)

    has_pair = (re.search(r"\b(отъезд|выезд|отправление)", text.lower())
                and re.search(r"\b(приезд|прибытие|возвращение)", text.lower()))

    notes = []
    if note:
        notes.append(note)

    if rng:
        hm, end_hm = rng
    elif has_pair and len(times) >= 2:
        hm, end_hm = times[0], times[-1]
    elif times:
        hm, end_hm = times[0], None
    elif daypart:
        hm, end_hm = daypart, None
    else:
        hm, end_hm = None, None

    if d is None and rrule is None:
        if hm is None:
            return None, None  # ничего календарного не найдено
        if inherited_date:
            d, kind = inherited_date, "explicit"
        else:
            return None, None  # время без даты — нераспознано

    if hm is None:
        hm = DEFAULT_TIME
        notes.append("Время не указано — утренний блок.")

    if rrule is not None and d is None:
        d = _rrule_start(byday, monthly_day, hm, base)
    elif kind == "weekday" and d == base.date() and (hm[0], hm[1]) <= (base.hour, base.minute):
        d += timedelta(days=7)  # сегодня этот день, но время уже прошло

    if end_hm is not None:
        duration = None
    elif duration is None:
        duration = DEFAULT_DURATION_MIN

    desc = "Из Telegram"
    for n in notes:
        desc += "\n" + n

    ev = {"summary": _title(t), "date": d.isoformat(),
          "time": f"{hm[0]:02d}:{hm[1]:02d}", "description": desc}
    if end_hm is not None:
        ev["end_time"] = f"{end_hm[0]:02d}:{end_hm[1]:02d}"
    else:
        ev["duration_min"] = duration
    if rrule:
        ev["rrule"] = rrule
    return ev, d


def parse_messages(messages):
    """Контракт как у claude_parser.parse_with_claude (см. модульный докстринг)."""
    events, unrecognized = [], []
    prev_dt, prev_date = None, None
    for msg in messages:
        base = datetime.strptime(msg["date_msk"], "%Y-%m-%d %H:%M:%S")
        inherited = None
        if prev_dt is not None and prev_date is not None:
            if (base - prev_dt) <= timedelta(minutes=FOLLOWUP_WINDOW_MIN):
                inherited = prev_date
        segments = [s for s in re.split(r"[;\n]+|(?<=[а-яa-z0-9])\.\s+",
                                        msg["text"]) if s.strip()]
        msg_events, seg_date = [], None
        for seg in segments:
            ev, d = _parse_segment(seg, base, seg_date or inherited)
            if ev:
                ev["source_message_id"] = msg["message_id"]
                msg_events.append(ev)
                if d and seg_date is None:
                    seg_date = d
        if msg_events:
            events.extend(msg_events)
            prev_dt = base
            prev_date = seg_date
        else:
            unrecognized.append(msg["message_id"])
            prev_dt, prev_date = base, prev_date
    return {"events": events, "unrecognized_message_ids": unrecognized}
