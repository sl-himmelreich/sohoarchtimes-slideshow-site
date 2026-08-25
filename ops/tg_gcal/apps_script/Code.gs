/**
 * SOHO Calendar Assistant — автономный планировщик (Google Apps Script).
 * Telegram -> Google Календарь, ежедневно ~21:00 МСК, без Claude и без ключей:
 * доступ к календарю у скрипта родной (запускается от имени владельца).
 *
 * УСТАНОВКА (один раз):
 *   1. Открыть https://script.google.com/create
 *   2. Стереть заглушку, вставить этот файл целиком.
 *   3. Ниже в TELEGRAM_BOT_TOKEN вставить токен бота (между кавычек).
 *      Рекомендуется: в DEEPSEEK_API_KEY вставить ключ DeepSeek — тогда
 *      разбор вольного текста делает DeepSeek (дёшево); без ключа работает
 *      встроенный парсер.
 *   4. Сохранить (Ctrl+S), в списке функций выбрать `setup`, нажать «Run»
 *      и разрешить доступ (Allow). Скрипт сразу разберёт накопившееся,
 *      пришлёт ✅ в Telegram и поставит себе ежедневный триггер ~21:00 МСК.
 *
 * ВЫКЛЮЧИТЬ ВСЁ: запустить функцию `disable` (или удалить проект скрипта).
 *
 * Правила разбора — ops/tg_gcal/PARSING_RULES.md (встроены ниже дословно
 * по смыслу). Дисциплина offset: подтверждение строго в конце безошибочного
 * запуска; при ошибке сообщения придут повторно в следующий запуск.
 */

// ==================== НАСТРОЙКА ====================
var TELEGRAM_BOT_TOKEN = 'ВСТАВЬТЕ_ТОКЕН_БОТА_СЮДА';
var DEEPSEEK_API_KEY = ''; // рекомендуется: разбор через DeepSeek (дёшево); иначе встроенный парсер
var DEEPSEEK_MODEL = 'deepseek-chat';
var ANTHROPIC_API_KEY = ''; // запасной вариант: разбор через Claude API
var PERSONAL_CHAT_ID = 1294602429; // единственный обрабатываемый чат
var GAS_MARKER = '[планировщик GAS]'; // метка в description для авто-отключения моста
var RUN_HOUR_MSK = 21;

// ==================== УПРАВЛЕНИЕ ====================
function setup() {
  if (!TELEGRAM_BOT_TOKEN || TELEGRAM_BOT_TOKEN.indexOf('ВСТАВЬТЕ') === 0) {
    throw new Error('Сначала вставьте токен бота в строку TELEGRAM_BOT_TOKEN.');
  }
  removeTriggers_();
  ScriptApp.newTrigger('runDaily')
    .timeBased().everyDays(1).atHour(RUN_HOUR_MSK).nearMinute(0)
    .inTimezone('Europe/Moscow').create();
  runDaily();
  tg_('sendMessage', { chat_id: PERSONAL_CHAT_ID,
    text: '✅ Автономный планировщик установлен: ежедневно ~21:00 МСК' });
}

function disable() {
  removeTriggers_();
  tg_('sendMessage', { chat_id: PERSONAL_CHAT_ID, text: '✅ Планировщик выключен' });
}

function removeTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'runDaily') ScriptApp.deleteTrigger(t);
  });
}

// ==================== ЕЖЕДНЕВНЫЙ ЗАПУСК ====================
function runDaily() {
  try {
    var data = fetchData_();
    if (!data.messages.length) {
      if (data.updates_total > 0) confirmOffset_(data.max_update_id + 1);
      return; // пустой запуск — полная тишина
    }
    var parsed = parseWithLlm_(data.messages) || parseMessages(data.messages);
    var cal = CalendarApp.getDefaultCalendar();
    var created = [];
    parsed.events.forEach(function (ev) {
      if (hasDuplicate_(cal, ev.date, ev.summary)) {
        console.log('дубль пропущен: ' + ev.date + ' «' + ev.summary + '»');
        return;
      }
      insertEvent_(cal, ev);
      created.push(ev);
      console.log('создано: ' + ev.date + ' ' + ev.time + ' «' + ev.summary + '»');
    });
    buildConfirmations(created, parsed.unrecognized_message_ids.length)
      .forEach(function (text) {
        tg_('sendMessage', { chat_id: PERSONAL_CHAT_ID, text: text });
      });
    confirmOffset_(data.max_update_id + 1);
    console.log('offset подтверждён: ' + (data.max_update_id + 1));
  } catch (e) {
    // offset не подтверждаем — сообщения придут повторно в следующий запуск
    console.error('запуск с ошибкой, offset не подтверждён: ' + e);
  }
}

// ==================== TELEGRAM ====================
function tg_(method, params) {
  // Тело строго в JSON: UrlFetchApp form-кодировкой ломает кириллицу/эмодзи,
  // и Telegram отвечает «chat not found». JSON-тело этого лишено.
  var resp = UrlFetchApp.fetch(
    'https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/' + method,
    { method: 'post', contentType: 'application/json',
      payload: JSON.stringify(params || {}), muteHttpExceptions: true });
  var data = JSON.parse(resp.getContentText());
  if (!data.ok) throw new Error(method + ' failed: ' + data.error_code + ' ' + data.description);
  return data.result;
}

function fetchData_() {
  if (tg_('getWebhookInfo').url) tg_('deleteWebhook', { drop_pending_updates: 'false' });
  var updates = tg_('getUpdates', { timeout: 0, limit: 100 });
  var maxId = null;
  updates.forEach(function (u) { if (maxId === null || u.update_id > maxId) maxId = u.update_id; });

  var byMid = {}; // последняя редакция каждого message_id
  updates.forEach(function (u) {
    var msg = u.message || u.edited_message;
    if (!msg) return; // channel_post и прочее — игнор
    if (!msg.chat || msg.chat.id !== PERSONAL_CHAT_ID) return;
    if (!msg.text || msg.text.charAt(0) === '/') return;
    var rev = msg.edit_date || 0;
    var cur = byMid[msg.message_id];
    if (!cur || rev >= cur.rev) byMid[msg.message_id] = { rev: rev, msg: msg };
  });

  var messages = Object.keys(byMid).map(Number).sort(function (a, b) { return a - b; })
    .map(function (mid) {
      var msg = byMid[mid].msg;
      var d = new Date((msg.date + 3 * 3600) * 1000); // МСК как UTC-компоненты
      var p2 = function (n) { return (n < 10 ? '0' : '') + n; };
      return {
        message_id: mid,
        date_msk: d.getUTCFullYear() + '-' + p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate())
          + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()) + ':' + p2(d.getUTCSeconds()),
        weekday_msk: WEEKDAYS_RU[(d.getUTCDay() + 6) % 7],
        text: msg.text
      };
    });

  return { updates_total: updates.length, max_update_id: maxId, messages: messages };
}

function confirmOffset_(offset) {
  tg_('getUpdates', { offset: offset, limit: 1, timeout: 0 });
}

// ==================== КАЛЕНДАРЬ ====================
function mskDate_(iso, hm) { // 'YYYY-MM-DD','HH:MM' (МСК) -> Date (абсолютный момент)
  var d = iso.split('-'), t = hm.split(':');
  return new Date(Date.UTC(+d[0], +d[1] - 1, +d[2], +t[0] - 3, +t[1]));
}

function hasDuplicate_(cal, dateIso, summary) {
  var p = dateIso.split('-');
  var start = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2], -3));
  var end = new Date(start.getTime() + 86400000);
  return cal.getEvents(start, end).some(function (e) { return similarTitles(summary, e.getTitle()); });
}

function insertEvent_(cal, ev) {
  var start = mskDate_(ev.date, ev.time);
  var end = ev.end_time
    ? mskDate_(ev.end_date || ev.date, ev.end_time)
    : new Date(start.getTime() + (ev.duration_min || 60) * 60000);
  var opts = { description: (ev.description || 'Из Telegram') + '\n' + GAS_MARKER };
  if (ev.rrule) {
    cal.createEventSeries(ev.summary, start, end, rruleToRecurrence_(ev.rrule), opts);
  } else {
    cal.createEvent(ev.summary, start, end, opts);
  }
}

function rruleToRecurrence_(rrule) {
  var body = rrule.replace(/^RRULE:/, '');
  var f = {};
  body.split(';').forEach(function (kv) { var p = kv.split('='); f[p[0]] = p[1]; });
  var rec = CalendarApp.newRecurrence(), rule;
  if (f.FREQ === 'DAILY') {
    rule = rec.addDailyRule();
  } else if (f.FREQ === 'WEEKLY') {
    rule = rec.addWeeklyRule();
    if (f.BYDAY) {
      var map = { MO: CalendarApp.Weekday.MONDAY, TU: CalendarApp.Weekday.TUESDAY,
        WE: CalendarApp.Weekday.WEDNESDAY, TH: CalendarApp.Weekday.THURSDAY,
        FR: CalendarApp.Weekday.FRIDAY, SA: CalendarApp.Weekday.SATURDAY,
        SU: CalendarApp.Weekday.SUNDAY };
      rule.onlyOnWeekdays(f.BYDAY.split(',').map(function (d) { return map[d]; }));
    }
  } else if (f.FREQ === 'MONTHLY') {
    rule = rec.addMonthlyRule();
    if (f.BYMONTHDAY) rule.onlyOnMonthDay(+f.BYMONTHDAY);
  } else {
    rule = rec.addDailyRule();
  }
  if (f.UNTIL) {
    var m = f.UNTIL.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/);
    if (m) rule.until(new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6])));
  }
  return rec;
}

// ==================== РАЗБОР ЧЕРЕЗ LLM (DeepSeek — основной, Claude — запасной) ====================
function parseWithLlm_(messages) {
  return parseWithDeepSeek_(messages) || parseWithClaude_(messages);
}

function validateLlm_(out) {
  if (!(out.events instanceof Array) || !(out.unrecognized_message_ids instanceof Array)) return null;
  for (var i = 0; i < out.events.length; i++) {
    var ev = out.events[i];
    if (!ev.summary || !/^\d{4}-\d{2}-\d{2}$/.test(ev.date) || !/^\d{2}:\d{2}$/.test(ev.time)) return null;
    if (!ev.description || ev.description.indexOf('Из Telegram') !== 0) {
      ev.description = ('Из Telegram\n' + (ev.description || '')).replace(/\n$/, '');
    }
  }
  return out;
}

// DeepSeek (api.deepseek.com, OpenAI-совместимый) — дёшево, приоритетный разбор
function parseWithDeepSeek_(messages) {
  if (!DEEPSEEK_API_KEY) return null;
  try {
    var resp = UrlFetchApp.fetch('https://api.deepseek.com/chat/completions', {
      method: 'post',
      contentType: 'application/json',
      headers: { Authorization: 'Bearer ' + DEEPSEEK_API_KEY },
      payload: JSON.stringify({
        model: DEEPSEEK_MODEL || 'deepseek-chat',
        temperature: 0,
        response_format: { type: 'json_object' },
        messages: [{ role: 'system', content: LLM_RULES_ + LLM_CONTRACT_ },
          { role: 'user', content: JSON.stringify(messages) }]
      }),
      muteHttpExceptions: true
    });
    if (resp.getResponseCode() !== 200) return null;
    var data = JSON.parse(resp.getContentText());
    var text = data.choices[0].message.content;
    return validateLlm_(JSON.parse(text.match(/\{[\s\S]*\}/)[0]));
  } catch (e) {
    console.error('deepseek parse: fallback: ' + e);
    return null;
  }
}

// Claude API — запасной разбор
function parseWithClaude_(messages) {
  if (!ANTHROPIC_API_KEY) return null;
  try {
    var resp = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
      method: 'post',
      contentType: 'application/json',
      headers: { 'x-api-key': ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      payload: JSON.stringify({
        model: 'claude-opus-5',
        max_tokens: 16000,
        system: LLM_RULES_ + LLM_CONTRACT_,
        messages: [{ role: 'user', content: JSON.stringify(messages) }]
      }),
      muteHttpExceptions: true
    });
    var data = JSON.parse(resp.getContentText());
    if (resp.getResponseCode() !== 200 || data.stop_reason === 'refusal') return null;
    var text = data.content.filter(function (b) { return b.type === 'text'; })
      .map(function (b) { return b.text; }).join('');
    return validateLlm_(JSON.parse(text.match(/\{[\s\S]*\}/)[0]));
  } catch (e) {
    console.error('claude parse: fallback: ' + e);
    return null;
  }
}

var LLM_CONTRACT_ = '\n---\nЗадача: разобрать входные сообщения Telegram в события календаря СТРОГО по правилам выше. Вход — JSON-список сообщений с полями message_id, date_msk («YYYY-MM-DD HH:MM:SS», МСК — база всех относительных дат этого сообщения), weekday_msk и text.\nОтвет — ТОЛЬКО валидный JSON без пояснений и без markdown-ограждений:\n{"events":[{"summary":"название по правилам","date":"YYYY-MM-DD","time":"HH:MM","duration_min":60,"end_date":"YYYY-MM-DD (опционально)","end_time":"HH:MM (опционально, вместо duration_min)","rrule":"RRULE:FREQ=... (опционально)","description":"Из Telegram... (всегда начинается с «Из Telegram»; сюда же строки про неуказанное время и «Контекст: «...»»)","source_message_id":123}],"unrecognized_message_ids":[124]}\nСообщение с несколькими делами даёт несколько объектов events. Никакого текста вне JSON.';

// ==================== ФОРМАТЫ ПОДТВЕРЖДЕНИЙ ====================
var WEEKDAYS_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

function isoWeekday_(iso) {
  var p = iso.split('-');
  return (new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])).getUTCDay() + 6) % 7;
}

function buildConfirmations(created, unrecognizedCount) {
  var out = [];
  var ddmm = function (iso) { var p = iso.split('-'); return p[2] + '.' + p[1]; };
  if (created.length === 1) {
    out.push('✅ Добавлено: ' + created[0].summary + ', ' + ddmm(created[0].date)
      + ', ' + created[0].time);
  } else if (created.length > 1) {
    var lines = ['✅ Добавлено ' + created.length + ' событий:'];
    created.forEach(function (ev) {
      lines.push('• ' + ddmm(ev.date) + ' (' + WEEKDAYS_RU[isoWeekday_(ev.date)] + ') '
        + ev.time + ' — ' + ev.summary);
    });
    out.push(lines.join('\n'));
  }
  for (var i = 0; i < unrecognizedCount; i++) {
    out.push('⚠️ Не удалось распознать событие. Пример формата: «3 апреля 14:00 30 мин встреча с Петровым»');
  }
  return out;
}

// ==================== СХОЖЕСТЬ НАЗВАНИЙ (дубликаты) ====================
function normTitle_(s) {
  return String(s || '').toLowerCase().replace(/ё/g, 'е')
    .replace(/[^a-zа-я0-9 ]/g, ' ').replace(/\s+/g, ' ').replace(/^\s+|\s+$/g, '');
}

function similarTitles(a, b) {
  a = normTitle_(a); b = normTitle_(b);
  if (!a || !b) return false;
  if (a === b) return true;
  var big = function (s) {
    var r = {};
    for (var i = 0; i < s.length - 1; i++) { var g = s.substr(i, 2); r[g] = (r[g] || 0) + 1; }
    return r;
  };
  var A = big(a), B = big(b), inter = 0, na = 0, nb = 0, g;
  for (g in A) { na += A[g]; if (B[g]) inter += Math.min(A[g], B[g]); }
  for (g in B) nb += B[g];
  if (!na || !nb) return false;
  return (2 * inter) / (na + nb) >= 0.8;
}

// ==================== ВСТРОЕННЫЙ ПАРСЕР (порт ops/tg_gcal/ru_parser.py) ====================
// Аварийный/основной (без API-ключа) разбор по PARSING_RULES.md. Всё, что не
// разобрано надёжно, помечается нераспознанным (⚠️) — это штатное поведение.

var DEFAULT_DURATION_MIN = 60;
var FOLLOWUP_WINDOW_MIN = 30;

var MONTHS_GEN = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
  'августа', 'сентября', 'октября', 'ноября', 'декабря'];
var MONTHS_PREP = ['январе', 'феврале', 'марте', 'апреле', 'мае', 'июне', 'июле',
  'августе', 'сентябре', 'октябре', 'ноябре', 'декабре'];
var WD_STEMS = ['понедельник(?:а|у)?', 'вторник(?:а|у)?', 'сред(?:а|у|е|ы)',
  'четверг(?:а|у)?', 'пятниц(?:а|у|е|ы)', 'суббот(?:а|у|е|ы)', 'воскресень(?:е|я|ю)'];
var WD_PLURAL = ['понедельникам', 'вторникам', 'средам', 'четвергам', 'пятницам',
  'субботам', 'воскресеньям'];
var BYDAY = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];

var WORD_UNITS = { 'ноль': 0, 'один': 1, 'одну': 1, 'одна': 1, 'два': 2, 'две': 2,
  'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8,
  'девять': 9, 'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
  'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15, 'шестнадцать': 16,
  'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19 };
var WORD_TENS = { 'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50 };

// Границы слов для кириллицы (\b в JS работает только с латиницей)
var B1 = '(?<![а-я0-9a-z])';
var B2 = '(?![а-я0-9a-z])';

function keys_(o) { return Object.keys(o); }
function wdRe_() {
  return WD_STEMS.map(function (s, i) { return '(?<wd' + i + '>' + s + ')'; }).join('|');
}
function wdPluralRe_() {
  return WD_PLURAL.map(function (s, i) { return '(?<wd' + i + '>' + s + ')'; }).join('|');
}

var COMMAND_PREFIX = new RegExp(
  '^\\s*(?:внеси(?:те)?|вынеси(?:те)?|неси|занеси|запиши(?:те)?|поставь(?:те)?|'
  + 'добавь(?:те)?|создай(?:те)?|внести|добавить|записать|поставить|создать)'
  + B2 + '(?:\\s+(?:в|на)\\s+календарь)?(?:\\s+(?:мне|пожалуйста))*'
  + '(?:\\s+(?:в|на|к)' + B2 + ')?\\s*[:,-]?\\s*', 'i');

function Txt_(text) {
  this.orig = text.split('');
  this.norm = text.toLowerCase().replace(/ё/g, 'е').split('');
}
Txt_.prototype.s = function () { return this.norm.join(''); };
Txt_.prototype.blank = function (start, end) {
  for (var i = start; i < end; i++) { this.norm[i] = ' '; this.orig[i] = ' '; }
};
Txt_.prototype.take = function (pattern) {
  var m = this.s().match(new RegExp(pattern));
  if (m) this.blank(m.index, m.index + m[0].length);
  return m;
};
Txt_.prototype.remainder = function () {
  return this.orig.join('').replace(/\s+/g, ' ')
    .replace(/^[\s,.;:—–-]+|[\s,.;:—–-]+$/g, '');
};

function wdIndex_(m) {
  for (var i = 0; i < 7; i++) if (m.groups && m.groups['wd' + i]) return i;
  return null;
}

function wordNumber_(tokens) {
  if (!tokens.length) return null;
  var t0 = tokens[0];
  if (t0 in WORD_TENS) {
    if (tokens.length > 1 && tokens[1] in WORD_UNITS && WORD_UNITS[tokens[1]] < 10) {
      return [WORD_TENS[t0] + WORD_UNITS[tokens[1]], 2];
    }
    return [WORD_TENS[t0], 1];
  }
  if (t0 in WORD_UNITS) return [WORD_UNITS[t0], 1];
  return null;
}

// --- даты как {y,m,d} ---
function dSer_(d) { return Date.UTC(d.y, d.m - 1, d.d) / 86400000; }
function dAdd_(d, n) {
  var x = new Date(Date.UTC(d.y, d.m - 1, d.d + n));
  return { y: x.getUTCFullYear(), m: x.getUTCMonth() + 1, d: x.getUTCDate() };
}
function dIso_(d) {
  var p2 = function (n) { return (n < 10 ? '0' : '') + n; };
  return d.y + '-' + p2(d.m) + '-' + p2(d.d);
}
function dWeekday_(d) { return (new Date(Date.UTC(d.y, d.m - 1, d.d)).getUTCDay() + 6) % 7; }
function dValid_(y, m, day) {
  var x = new Date(Date.UTC(y, m - 1, day));
  return x.getUTCFullYear() === y && x.getUTCMonth() === m - 1 && x.getUTCDate() === day;
}

function parseBase_(dateMsk) { // 'YYYY-MM-DD HH:MM:SS'
  var m = dateMsk.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/);
  return { date: { y: +m[1], m: +m[2], d: +m[3] }, h: +m[4], mi: +m[5],
    wd: dWeekday_({ y: +m[1], m: +m[2], d: +m[3] }) };
}

function nearestFutureDate_(day, month, base, year) {
  if (year) return { y: year, m: month, d: day };
  var cand = { y: base.date.y, m: month, d: day };
  if (dSer_(cand) < dSer_(base.date)) cand = { y: base.date.y + 1, m: month, d: day };
  return cand;
}

function nearestDom_(day, base) {
  var y = base.date.y, m = base.date.m;
  for (var i = 0; i < 24; i++) {
    if (dValid_(y, m, day)) {
      var cand = { y: y, m: m, d: day };
      if (dSer_(cand) > dSer_(base.date)) return cand;
    }
    m++; if (m === 13) { y++; m = 1; }
  }
  throw new Error('нет подходящей даты');
}

function monthEndUntil_(month, base) {
  var y = month >= base.date.m ? base.date.y : base.date.y + 1;
  var nmY = month < 12 ? y : y + 1, nmM = month < 12 ? month + 1 : 1;
  var end = new Date(Date.UTC(nmY, nmM - 1, 1, 0, 0, 0) - 1000 - 3 * 3600 * 1000);
  var p2 = function (n) { return (n < 10 ? '0' : '') + n; };
  return '' + end.getUTCFullYear() + p2(end.getUTCMonth() + 1) + p2(end.getUTCDate())
    + 'T' + p2(end.getUTCHours()) + p2(end.getUTCMinutes()) + p2(end.getUTCSeconds()) + 'Z';
}

function extractRrule_(t, base) {
  var until = '';
  var mm = t.s().match(new RegExp(B1 + 'в\\s+(' + MONTHS_PREP.join('|') + ')' + B2));
  var scopeMonth = mm ? MONTHS_PREP.indexOf(mm[1]) + 1 : null;
  var eatScope = function () {
    if (scopeMonth) {
      until = ';UNTIL=' + monthEndUntil_(scopeMonth, base);
      t.take(B1 + 'в\\s+(' + MONTHS_PREP.join('|') + ')' + B2);
    }
  };

  if (t.take(B1 + '(?:ежедневно|каждый\\s+день)' + B2)) {
    eatScope();
    return { rrule: 'RRULE:FREQ=DAILY' + until, byday: null, dom: null };
  }
  if (t.take(B1 + 'по\\s+будням' + B2)) {
    eatScope();
    return { rrule: 'RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR' + until,
      byday: [0, 1, 2, 3, 4], dom: null };
  }
  var m = t.take(B1 + 'кажд(?:ый|ую|ое)\\s+(?:' + wdRe_() + ')' + B2);
  if (!m) m = t.take(B1 + 'по\\s+(?:' + wdPluralRe_() + ')' + B2);
  if (m) {
    var i = wdIndex_(m);
    eatScope();
    return { rrule: 'RRULE:FREQ=WEEKLY;BYDAY=' + BYDAY[i] + until, byday: [i], dom: null };
  }
  m = t.take(B1 + '(\\d{1,2})\\s+числа\\s+каждого\\s+месяца' + B2);
  if (m) {
    return { rrule: 'RRULE:FREQ=MONTHLY;BYMONTHDAY=' + (+m[1]) + until, byday: null, dom: +m[1] };
  }
  return { rrule: null, byday: null, dom: null };
}

function extractDate_(t, base) {
  var note = '';
  var m = t.take(B1 + '(\\d{1,2})\\.(\\d{1,2})\\.(\\d{4})' + B2);
  if (m) return { d: { y: +m[3], m: +m[2], d: +m[1] }, kind: 'explicit', note: note };

  m = t.take(B1 + '(\\d{1,2})\\s+(' + MONTHS_GEN.join('|') + ')(?:\\s+(\\d{4}))?' + B2);
  if (m) {
    return { d: nearestFutureDate_(+m[1], MONTHS_GEN.indexOf(m[2]) + 1, base,
      m[3] ? +m[3] : null), kind: 'explicit', note: note };
  }

  m = t.take(B1 + '(\\d{1,2})\\s+числа' + B2 + '(?!\\s+каждого)');
  if (m) return { d: nearestDom_(+m[1], base), kind: 'explicit', note: note };

  var rel = null;
  if (t.take(B1 + 'послезавтра' + B2)) rel = dAdd_(base.date, 2);
  else if (t.take(B1 + 'завтра' + B2)) rel = dAdd_(base.date, 1);
  else if (t.take(B1 + 'сегодня' + B2)) rel = dAdd_(base.date, 0);
  else {
    m = t.take(B1 + 'через\\s+(\\d{1,3}|' + keys_(WORD_TENS).concat(keys_(WORD_UNITS)).join('|')
      + ')\\s+(?:день|дня|дней)' + B2);
    if (m) {
      var tok = m[1];
      var n = /^\d+$/.test(tok) ? +tok : (WORD_TENS[tok] !== undefined ? WORD_TENS[tok] : WORD_UNITS[tok]);
      rel = dAdd_(base.date, n);
    }
  }

  var wdDate = null;
  m = t.take('(?:' + B1 + '(?:в|во|на)\\s+)?' + B1 + '(?:' + wdRe_() + ')\\s+на\\s+следующей\\s+неделе' + B2);
  if (!m) m = t.take(B1 + 'следующ(?:ий|ую|ее|ей)\\s+(?:в\\s+|во\\s+)?(?:' + wdRe_() + ')' + B2);
  if (m) {
    wdDate = dAdd_(base.date, (7 - base.wd) + wdIndex_(m));
  } else {
    m = t.take('(?:' + B1 + '(?:в|во|на)\\s+)?' + B1 + '(?:' + wdRe_() + ')\\s+на\\s+этой\\s+неделе' + B2);
    if (m) {
      wdDate = dAdd_(base.date, wdIndex_(m) - base.wd);
      if (dSer_(wdDate) < dSer_(base.date)) wdDate = dAdd_(wdDate, 7);
    } else {
      m = t.take(B1 + '(?:в|во|на)\\s+(?:' + wdRe_() + ')' + B2);
      if (m) {
        var delta = ((wdIndex_(m) - base.wd) % 7 + 7) % 7;
        wdDate = dAdd_(base.date, delta); // delta 0 = сегодня; уточнится по времени
      }
    }
  }

  if (wdDate && rel !== null) {
    var days = dSer_(rel) - dSer_(base.date);
    var word = days === 1 ? 'завтра' : days === 2 ? 'послезавтра'
      : days === 0 ? 'сегодня' : 'оговорка о дате';
    return { d: wdDate, kind: 'weekday', note: 'Контекст: «' + word + '».' };
  }
  if (wdDate) return { d: wdDate, kind: 'weekday', note: note };
  if (rel !== null) return { d: rel, kind: 'explicit', note: note };

  m = t.take(B1 + '(\\d{1,2})\\.(0[1-9]|1[0-2])' + B2 + '(?!\\.)');
  if (m && +m[1] <= 31) {
    return { d: nearestFutureDate_(+m[1], +m[2], base, null), kind: 'explicit', note: note };
  }
  return { d: null, kind: null, note: note };
}

function hoursShift_(h, suffix) {
  if (suffix === 'утра') return h;
  if (suffix === 'дня') return h < 12 ? h + 12 : h;
  if (suffix === 'вечера') return h < 12 ? h + 12 : h;
  if (suffix === 'ночи') return h === 12 ? 0 : h;
  return h;
}

function extractRange_(t) {
  var m = t.take(B1 + 'с\\s+(\\d{1,2})(?::(\\d{2}))?\\s+до\\s+(\\d{1,2})(?::(\\d{2}))?' + B2);
  if (m) return [[+m[1], +(m[2] || 0)], [+m[3], +(m[4] || 0)]];
  m = t.take(B1 + '(\\d{1,2}):(\\d{2})\\s*[-–—]\\s*(\\d{1,2}):(\\d{2})' + B2);
  if (m) return [[+m[1], +m[2]], [+m[3], +m[4]]];
  return null;
}

function extractTimes_(t) {
  var out = [];
  ['(\\d{1,2}):(\\d{2})', '(\\d{1,2})-([0-5]\\d)', '(\\d{1,2})\\.([0-5]\\d)']
    .forEach(function (pat) {
      while (true) {
        var m = t.take(B1 + pat + B2);
        if (!m) break;
        if (+m[1] <= 23) out.push([+m[1], +m[2], m.index]);
      }
    });
  var m = t.take(B1 + '(?:в\\s+)?(\\d{1,2})\\s+час(?:а|ов)?(?:\\s+(\\d{1,2})\\s+минут[уы]?)?' + B2);
  if (m) out.push([+m[1], +(m[2] || 0), m.index]);
  while (true) {
    m = t.take(B1 + '(?:в\\s+)?(\\d{1,2})\\s+(утра|дня|вечера|ночи)' + B2);
    if (!m) break;
    out.push([hoursShift_(+m[1], m[2]), 0, m.index]);
  }
  var words = keys_(WORD_TENS).concat(keys_(WORD_UNITS)).join('|');
  var units = keys_(WORD_UNITS).filter(function (u) { return WORD_UNITS[u] < 10; }).join('|');
  m = t.take(B1 + '(?:в\\s+)?(' + words + ')(?:\\s+(' + words + '))?\\s+(утра|дня|вечера|ночи)' + B2);
  if (m) {
    var toks = [m[1], m[2]].filter(Boolean);
    var val = wordNumber_(toks);
    if (val && val[0] <= 12) out.push([hoursShift_(val[0], m[3]), 0, m.index]);
  }
  m = t.take(B1 + '(' + words + ')(?:\\s+(' + units + '))?\\s+(' + words + ')(?:\\s+(' + units + '))?' + B2);
  if (m) {
    var toks2 = [m[1], m[2], m[3], m[4]].filter(Boolean);
    var h = wordNumber_(toks2);
    if (h) {
      var rest = toks2.slice(h[1]);
      var mi = wordNumber_(rest);
      if (mi && h[0] <= 23 && mi[0] <= 59 && rest.length === mi[1]) {
        out.push([h[0], mi[0], m.index]);
      }
    }
  }
  out.sort(function (a, b) { return a[2] - b[2]; });
  return out.map(function (x) { return [x[0], x[1]]; });
}

function extractDaypart_(t) {
  if (t.take(B1 + 'утром' + B2)) return [9, 0];
  if (t.take(B1 + 'днем' + B2)) return [13, 0];
  if (t.take(B1 + 'вечером' + B2)) return [19, 0];
  if (t.take(B1 + 'ночью' + B2)) return [22, 0];
  return null;
}

function extractDuration_(t) {
  if (t.take(B1 + '(?:на\\s+)?полтора\\s+часа' + B2)) return 90;
  if (t.take(B1 + '(?:на\\s+)?полчаса' + B2)) return 30;
  var m = t.take(B1 + '(\\d{1,3})\\s*(?:мин(?:ут[уы]?)?\\.?)' + B2);
  if (m) return +m[1];
  m = t.take(B1 + '(?:на\\s+)?(\\d{1,2})\\s*час(?:а|ов)?' + B2);
  if (m) return +m[1] * 60;
  if (t.take(B1 + 'на\\s+час' + B2)) return 60;
  return null;
}

function makeTitle_(t) {
  var raw = t.remainder().replace(COMMAND_PREFIX, '')
    .replace(/\s+/g, ' ').replace(/^[\s,.;:—–-]+|[\s,.;:—–-]+$/g, '');
  if (!raw) return 'Событие';
  return raw.charAt(0).toUpperCase() + raw.slice(1);
}

function rruleStart_(byday, dom, hm, base) {
  if (dom) return nearestDom_(dom, base);
  if (byday !== null) {
    var best = null;
    byday.forEach(function (i) {
      var delta = ((i - base.wd) % 7 + 7) % 7;
      var cand = dAdd_(base.date, delta);
      if (delta === 0 && (hm[0] < base.h || (hm[0] === base.h && hm[1] <= base.mi))) {
        cand = dAdd_(cand, 7);
      }
      if (best === null || dSer_(cand) < dSer_(best)) best = cand;
    });
    return best;
  }
  var d = base.date;
  if (hm[0] < base.h || (hm[0] === base.h && hm[1] <= base.mi)) d = dAdd_(d, 1);
  return d;
}

function parseSegment_(text, base, inheritedDate) {
  var t = new Txt_(text);
  var rr = extractRrule_(t, base);
  var dd = extractDate_(t, base);
  var rng = extractRange_(t);
  var times = extractTimes_(t);
  var daypart = extractDaypart_(t);
  var duration = extractDuration_(t);

  var low = text.toLowerCase();
  var hasPair = /(отъезд|выезд|отправление)/.test(low) && /(приезд|прибытие|возвращение)/.test(low);

  var notes = [];
  if (dd.note) notes.push(dd.note);

  var hm = null, endHm = null;
  if (rng) { hm = rng[0]; endHm = rng[1]; }
  else if (hasPair && times.length >= 2) { hm = times[0]; endHm = times[times.length - 1]; }
  else if (times.length) { hm = times[0]; }
  else if (daypart) { hm = daypart; }

  var d = dd.d, kind = dd.kind;
  if (d === null && rr.rrule === null) {
    if (hm === null) return null;
    if (inheritedDate) { d = inheritedDate; kind = 'explicit'; }
    else return null; // время без даты — нераспознано
  }

  if (hm === null) {
    hm = [9, 0];
    notes.push('Время не указано — утренний блок.');
  }

  if (rr.rrule !== null && d === null) {
    d = rruleStart_(rr.byday, rr.dom, hm, base);
  } else if (kind === 'weekday' && d !== null && dSer_(d) === dSer_(base.date)
    && (hm[0] < base.h || (hm[0] === base.h && hm[1] <= base.mi))) {
    d = dAdd_(d, 7); // сегодня этот день, но время уже прошло
  }

  if (endHm !== null) duration = null;
  else if (duration === null) duration = DEFAULT_DURATION_MIN;

  var desc = 'Из Telegram';
  notes.forEach(function (n) { desc += '\n' + n; });

  var p2 = function (n) { return (n < 10 ? '0' : '') + n; };
  var ev = { summary: makeTitle_(t), date: dIso_(d),
    time: p2(hm[0]) + ':' + p2(hm[1]), description: desc };
  if (endHm !== null) ev.end_time = p2(endHm[0]) + ':' + p2(endHm[1]);
  else ev.duration_min = duration;
  if (rr.rrule) ev.rrule = rr.rrule;
  return { ev: ev, d: d };
}

function parseMessages(messages) {
  var events = [], unrecognized = [];
  var prevBaseMin = null, prevDate = null;
  messages.forEach(function (msg) {
    var base = parseBase_(msg.date_msk);
    var baseMin = dSer_(base.date) * 1440 + base.h * 60 + base.mi;
    var inherited = null;
    if (prevBaseMin !== null && prevDate !== null
      && baseMin - prevBaseMin <= FOLLOWUP_WINDOW_MIN) {
      inherited = prevDate;
    }
    var segments = msg.text.split(/[;\n]+|(?<=[а-яa-z0-9])\.\s+/i)
      .filter(function (s) { return s.trim(); });
    var msgEvents = [], segDate = null;
    segments.forEach(function (seg) {
      var res = parseSegment_(seg, base, segDate || inherited);
      if (res) {
        res.ev.source_message_id = msg.message_id;
        msgEvents.push(res.ev);
        if (res.d && segDate === null) segDate = res.d;
      }
    });
    if (msgEvents.length) {
      events = events.concat(msgEvents);
      prevBaseMin = baseMin;
      prevDate = segDate;
    } else {
      unrecognized.push(msg.message_id);
      prevBaseMin = baseMin;
    }
  });
  return { events: events, unrecognized_message_ids: unrecognized };
}

// ==================== ПРАВИЛА ДЛЯ LLM-РАЗБОРА (дословно) ====================
var LLM_RULES_ = [
  '# Правила разбора сообщений в события (НЕ МЕНЯТЬ)',
  '',
  'Константы: обрабатывается только чат 1294602429; TZ Europe/Moscow (+03:00); длительность по умолчанию 60 мин; дата без времени -> 09:00; description всегда начинается с «Из Telegram».',
  'База ВСЕХ относительных дат — date_msk сообщения (МСК), НЕ момент запуска.',
  '',
  '## Даты',
  '- «N месяца» / «N.MM» / «DD.MM.YYYY» — как написано; без года — ближайшая будущая.',
  '- «N числа» — ближайшее N-е (прошло — следующий месяц).',
  '- «сегодня / завтра / послезавтра / через N дней» — от даты сообщения.',
  '- День недели («в среду») — ближайший будущий; если сегодня этот день и время впереди — сегодня.',
  '- «следующий вторник» / «во вторник на следующей неделе» — день следующей календарной недели (недели с понедельника).',
  '',
  '## Время',
  '- HH:MM / HH-MM / HH.MM / «HH часов MM минут».',
  '- «HH утра» (06–11), «HH дня» (12–17), «HH вечера» (HH+12), «HH ночи» (00–05).',
  '- Числительные словами из диктовки («двадцать один тридцать» -> 21:30).',
  '- «утром» -> 09:00, «днём» -> 13:00, «вечером» -> 19:00, «ночью» -> 22:00.',
  '- Времени нет -> 09:00, в description добавить «Время не указано — утренний блок.»',
  '',
  '## Длительность',
  '- «N мин / N часов»; «полчаса» = 30; «час» = 60; «полтора часа» = 90.',
  '- Диапазон «с 14 до 16» / «14:00–16:00» -> start/end по диапазону; не указана -> 60 мин.',
  '',
  '## Повторы',
  '- «ежедневно» -> RRULE:FREQ=DAILY; «каждый понедельник» / «по понедельникам» -> RRULE:FREQ=WEEKLY;BYDAY=MO (аналогично остальным дням); «по будням» -> BYDAY=MO,TU,WE,TH,FR.',
  '- «N числа каждого месяца» -> RRULE:FREQ=MONTHLY;BYMONTHDAY=N, первое срабатывание — ближайшее будущее N-е.',
  '- Ограничение периода («в августе по понедельникам») -> добавить UNTIL (UTC).',
  '',
  '## Структура',
  '- Несколько дел в одном сообщении -> отдельные события; «14:00 отъезд, 20:00 приезд» -> одно событие 14:00–20:00.',
  '- Сообщение-уточнение без даты в пределах ~30 мин — трактовать в контексте предыдущего.',
  '- Лишняя оговорка («завтра» при явном дне недели) — дата из дня недели, оговорку в description: «Контекст: «…»».',
  '',
  '## Название',
  '- Суть после даты/времени; убрать стартовые «внеси / запиши / поставь / добавь / создай» (и искажения диктовки вроде «неси/вынеси в календарь»); первая буква заглавная.',
  '',
  '## Не событие',
  '- Приветствие, вопрос, обсуждение прошедшего без «внеси/запиши» -> в unrecognized_message_ids (ответ ⚠️).',
  '- Если дата есть, а неоднозначно только время — событие создать с 09:00, без ⚠️.'
].join('\n');

// ==================== ЭКСПОРТ ДЛЯ ТЕСТОВ (в Apps Script не используется) ====================
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    parseMessages: parseMessages,
    buildConfirmations: buildConfirmations,
    similarTitles: similarTitles
  };
}
