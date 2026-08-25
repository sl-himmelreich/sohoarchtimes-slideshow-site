#!/usr/bin/env node
// Тесты встроенного парсера Apps Script-версии (node ops/tg_gcal/tests_gs_parser.js).
// Зеркалят tests_ru_parser.py — обе реализации обязаны давать одинаковый результат.

const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'apps_script', 'Code.gs'), 'utf8');
const mod = { exports: {} };
new Function('module', src)(mod);
const { parseMessages, buildConfirmations, similarTitles } = mod.exports;

const BASE = '2026-08-24 22:11:32'; // понедельник
let failed = 0;

function one(text, dateMsk = BASE, mid = 1) {
  return parseMessages([{ message_id: mid, date_msk: dateMsk, text }]);
}
function ev(res, i = 0) {
  if (!res.events.length) throw new Error('нет событий: ' + JSON.stringify(res));
  return res.events[i];
}
function t(name, cond) {
  console.log((cond ? 'OK  ' : 'FAIL') + ' ' + name);
  if (!cond) failed++;
}

let r = ev(one('Неси в календарь в четверг на этой неделе 11:00 Генриху выезд в школу на репетицию'));
t('реальное сообщение: дата', r.date === '2026-08-27');
t('реальное сообщение: время', r.time === '11:00');
t('реальное сообщение: длительность', r.duration_min === 60);
t('реальное сообщение: название', r.summary === 'Генриху выезд в школу на репетицию');

r = ev(one('3 апреля 14:00 30 мин встреча с Петровым'));
t('пример формата: дата (ближайшая будущая)', r.date === '2027-04-03');
t('пример формата: время и 30 мин', r.time === '14:00' && r.duration_min === 30);
t('пример формата: название', r.summary === 'Встреча с Петровым');

r = ev(one('Внеси на завтра 15:00 тест переноса'));
t('завтра: дата', r.date === '2026-08-25');
t('завтра: название без командного глагола', r.summary === 'Тест переноса');

r = ev(one('в среду вечером ужин'));
t('день недели + вечером', r.date === '2026-08-26' && r.time === '19:00');

r = ev(one('каждый понедельник 10:00 планёрка'));
t('повтор: RRULE', r.rrule === 'RRULE:FREQ=WEEKLY;BYDAY=MO');
t('повтор: старт следующий пн (время прошло)', r.date === '2026-08-31');

r = ev(one('по будням 8:30 зарядка'));
t('будни: RRULE', r.rrule === 'RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR');
t('будни: старт завтра (вт)', r.date === '2026-08-25');

r = ev(one('послезавтра с 14 до 16 презентация'));
t('диапазон: дата', r.date === '2026-08-26');
t('диапазон: конец', r.time === '14:00' && r.end_time === '16:00');

r = ev(one('25 числа 21:00 кино'));
t('N числа: ближайшее 25-е', r.date === '2026-08-25');

r = ev(one('1 сентября 09:00 линейка'));
t('N месяца', r.date === '2026-09-01');

r = ev(one('завтра сдать отчёт'));
t('дата без времени -> 09:00', r.time === '09:00');
t('дата без времени -> пометка', r.description.includes('Время не указано'));
t('description начинается с «Из Telegram»', r.description.startsWith('Из Telegram'));

r = ev(one('в пятницу в 9 вечера кино'));
t('9 вечера = 21:00', r.date === '2026-08-28' && r.time === '21:00');

r = ev(one('запиши на 30.08 поездка на дачу'));
t('DD.MM', r.date === '2026-08-30');

r = ev(one('через 3 дня 12:00 обед с командой'));
t('через N дней', r.date === '2026-08-27' && r.time === '12:00');

r = ev(one('во вторник на следующей неделе 18:00 стрижка'));
t('следующая неделя', r.date === '2026-09-01');

r = ev(one('5 числа каждого месяца 10:00 оплата счетов'));
t('ежемесячно: RRULE', r.rrule === 'RRULE:FREQ=MONTHLY;BYMONTHDAY=5');
t('ежемесячно: старт ближайшее 5-е', r.date === '2026-09-05');

let res = one('Привет, как дела?');
t('не событие -> нераспознано',
  res.events.length === 0 && String(res.unrecognized_message_ids) === '1');

res = parseMessages([
  { message_id: 1, date_msk: '2026-08-24 22:11:32', text: 'завтра 15:00 врач' },
  { message_id: 2, date_msk: '2026-08-24 22:20:00', text: 'и в 18:00 аптека' },
]);
t('уточнение в пределах 30 мин наследует дату',
  res.events.length === 2 && res.events[1].date === '2026-08-25'
  && res.events[1].time === '18:00');

r = ev(one('завтра 14:00 отъезд, 20:00 приезд'));
t('отъезд/приезд: одно событие 14-20',
  r.date === '2026-08-25' && r.time === '14:00' && r.end_time === '20:00');

res = one('в 15:00 что-то без даты');
t('время без даты и без контекста -> нераспознано',
  res.events.length === 0 && String(res.unrecognized_message_ids) === '1');

r = ev(one('завтра в 21 час 30 минут созвон с мамой'));
t('HH часов MM минут', r.time === '21:30');

r = ev(one('Вынеси на пятницу в 14:00 завтра едем к Юленьке', '2026-08-25 02:51:20'));
t('пятница против «завтра»: дата из дня недели', r.date === '2026-08-28' && r.time === '14:00');
t('оговорка в description', r.description.includes('Контекст: «завтра»'));
t('название «Едем к Юленьке»', r.summary === 'Едем к Юленьке');

// форматы подтверждений
const evs = [
  { summary: 'Генриху выезд', date: '2026-08-27', time: '11:00' },
  { summary: 'Врач', date: '2026-09-01', time: '18:30' },
];
t('формат одного события',
  buildConfirmations(evs.slice(0, 1), 0)[0] === '✅ Добавлено: Генриху выезд, 27.08, 11:00');
const multi = buildConfirmations(evs, 1);
t('формат нескольких: заголовок', multi[0].startsWith('✅ Добавлено 2 событий:'));
t('формат нескольких: строка', multi[0].includes('• 27.08 (Чт) 11:00 — Генриху выезд'));
t('формат ⚠️', multi[1].startsWith('⚠️ Не удалось распознать событие.'));

// дубликаты
t('дубль: почти то же название', similarTitles('Едем к Юленьке', 'едем к юленьке!') === true);
t('не дубль: разные названия', similarTitles('Едем к Юленьке', 'Заказать автомобиль для Юленьки') === false);

if (failed) { console.log(failed + ' тестов упало'); process.exit(1); }
console.log('Все тесты пройдены.');
