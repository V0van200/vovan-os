// Vovan OS — живые данные в хабе (Claude). Отдельный модуль: код Astra не меняет.
// Источник: ./live/projects.json (collector/live.py, обновляется каждую минуту на сервере 78).
// Что делает: 1) значок «ЖИВЫЕ ДАННЫЕ · чч:мм» вместо «ЛОКАЛЬНО»; 2) блок «Сейчас» в паспорте проекта;
// 3) раз в минуту обновляет открытый паспорт. Когда Astra встроит live в свой интерфейс — этот файл можно убрать.
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
let live = null, lastId = null, loadedAt = null;

async function load() {
  try {
    const r = await fetch('./live/projects.json', { cache: 'no-store' });
    if (!r.ok) throw Error(r.status);
    live = await r.json(); loadedAt = new Date();
  } catch { live = null; }
  badge(); refreshOpen(); home();
}

const hhmm = iso => { const d = new Date(iso); return Number.isNaN(d.valueOf()) ? '' : d.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' }); };
const fresh = () => live && Date.now() - new Date(live.updated).valueOf() < 5 * 60e3;

function badge() {
  for (const el of document.querySelectorAll('body *')) {
    if (el.children.length > 1 || el.dataset.vlBadge) continue;
    if (/^\s*(ЛОКАЛЬНО|ЖИВЫЕ ДАННЫЕ.*)\s*$/i.test(el.textContent)) {
      el.dataset.vlBadge = '1';
      el.textContent = live ? (fresh() ? `ЖИВЫЕ ДАННЫЕ · ${hhmm(live.updated)}` : `ДАННЫЕ УСТАРЕЛИ · ${hhmm(live.updated)}`) : 'СНИМОК';
      el.closest('[class]')?.classList.toggle('vl-stale', !fresh());
      break;
    }
  }
  document.querySelectorAll('[data-vl-badge]').forEach(el => {
    el.textContent = live ? (fresh() ? `ЖИВЫЕ ДАННЫЕ · ${hhmm(live.updated)}` : `ДАННЫЕ УСТАРЕЛИ · ${hhmm(live.updated)}`) : 'СНИМОК';
  });
}

function spark(points) {
  if (!points?.length) return '';
  const max = Math.max(1, ...points.map(p => p[1])), w = 100 / points.length;
  const bars = points.map((p, i) => `<rect x="${i * w + w * 0.15}" y="${40 - (p[1] / max) * 38}" width="${w * 0.7}" height="${(p[1] / max) * 38 + 0.5}" rx="0.6"><title>${esc(p[0])}: ${esc(p[1])}</title></rect>`).join('');
  return `<svg class="vl-spark" viewBox="0 0 100 40" preserveAspectRatio="none" aria-hidden="true">${bars}</svg><div class="vl-spark-axis"><span>${esc(points[0][0])}</span><span>${esc(points.at(-1)[0])}</span></div>`;
}

function panel(id) {
  const p = live?.projects?.[id];
  if (!p) return `<section class="vl-panel vl-muted"><h3>Сейчас</h3><p>Живых данных по этому проекту нет.</p></section>`;
  const metrics = (p.metrics || []).map(m => `<div class="vl-metric ${m.level ? 'vl-' + esc(m.level) : ''}"><span>${esc(m.label)}</span><strong>${esc(m.value)}</strong>${m.hint ? `<small>${esc(m.hint)}</small>` : ''}</div>`).join('');
  const alerts = (p.alerts || []).map(a => `<div class="vl-alert">⚠ ${esc(a)}</div>`).join('');
  const series = (p.series || []).map(s => `<div class="vl-series"><h4>${esc(s.title)}</h4>${s.points?.length > 1 ? spark(s.points) : '<p class="vl-note">Данные копятся с сегодняшнего дня — график появится завтра.</p>'}</div>`).join('');
  const lists = (p.lists || []).filter(l => l.items?.length).map(l => `<div class="vl-list"><h4>${esc(l.title)}</h4><ul>${l.items.map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>`).join('');
  const preview = p.preview && /^https:\/\//.test(p.preview) ? `<div class="vl-preview"><h4>Сайт сейчас</h4><iframe src="${esc(p.preview)}" loading="lazy" referrerpolicy="no-referrer" sandbox="allow-scripts allow-same-origin" title="Предпросмотр сайта"></iframe><a href="${esc(p.preview)}" target="_blank" rel="noopener noreferrer">Открыть сайт ↗</a></div>` : '';
  return `<section class="vl-panel" data-vl-panel="${esc(id)}">
    <div class="vl-head"><h3>Сейчас${p.summary ? ` · ${esc(p.summary)}` : ''}</h3><span class="vl-time ${fresh() ? '' : 'vl-old'}">${p.connected ? '● ' : '○ '}обновлено ${esc(hhmm(p.updated))}</span></div>
    ${alerts}<div class="vl-body ${preview ? 'vl-with-preview' : ''}"><div><div class="vl-metrics">${metrics || '<p class="vl-note">Отдельный источник ещё не подключён — показано только состояние сервисов.</p>'}</div>${series}${lists}${p.note ? `<p class="vl-note">${esc(p.note)}</p>` : ''}</div>${preview}</div>
  </section>`;
}

// ── Главная: блок Terraria и счётчик ошибок ──
const isHome = () => ['', '#', '#home', '#/home'].includes(location.hash);
function homeTerraria() {
  const t = live?.projects?.terraria;
  if (!t) return '';
  const w = t.world || {}, accs = t.accounts || [], on = (t.online_names || []);
  const m = l => (t.metrics || []).find(x => x.label === l)?.value ?? '—';
  const running = !(t.alerts || []).some(a => a.includes('остановлен'));
  const row = a => `<tr><td>${a.online ? '<i class="vl-dot vl-on"></i>' : '<i class="vl-dot"></i>'}${esc(a.name)}</td><td>${esc(a.group)}</td><td>❤ ${esc(a.hp ?? '—')}/${esc(a.max_hp ?? '—')}</td><td>★ ${esc(a.mana ?? '—')}/${esc(a.max_mana ?? '—')}</td><td>${esc(a.deaths ?? 0)}</td><td>${esc(a.last ? new Date(a.last + 'Z').toLocaleString('ru', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—')}</td></tr>`;
  const list = title => (t.lists || []).find(l => l.title === title)?.items || [];
  return `<section class="vl-home" data-vl-home>
    <div class="vl-home-head">
      <div><h2>Terraria · ${esc(w.name || 'мир')}</h2><p>${esc(w.size || '')}${w.mode ? ' · сложность ' + esc(w.mode) : ''}${w.special?.length ? ' · ' + esc(w.special.join(', ')) : ''}${w.seed ? ' · сид ' + esc(w.seed) : ''}</p></div>
      <div class="vl-home-status ${running ? 'vl-ok' : 'vl-bad'}">${running ? '● Сервер работает' : '● Сервер остановлен'}<small>${esc(w.address || '')} · обновлено ${esc(hhmm(t.updated))}</small></div>
    </div>
    ${(t.alerts || []).map(a => `<div class="vl-alert">⚠ ${esc(a)}</div>`).join('')}
    <div class="vl-home-stats">
      <div><span>Онлайн</span><strong>${esc(m('Онлайн сейчас'))}</strong><small>${esc(on.join(', ') || 'никого')}</small></div>
      <div><span>Аккаунтов</span><strong>${esc(accs.length)}</strong><small>вход по паролю: ${w.require_login ? 'да' : 'нет'}</small></div>
      <div><span>Последний вход</span><strong>${esc(m('Последний вход'))}</strong></div>
      <div><span>Мир сохранён</span><strong>${esc(m('Сохранение мира'))}</strong></div>
      <div><span>Защита спавна</span><strong>${w.spawn_protection ? esc(w.spawn_protection) + ' блоков' : 'нет'}</strong><small>нельзя ломать и строить</small></div>
      <div><span>Бэкапы</span><strong>${esc(m('Бэкапы'))}</strong></div>
    </div>
    <div class="vl-home-cols">
      <div><h4>Игроки</h4>${accs.length ? `<div class="vl-tablewrap"><table class="vl-table"><thead><tr><th>Аккаунт</th><th>Группа</th><th>Здоровье</th><th>Мана</th><th>Смертей</th><th>Был</th></tr></thead><tbody>${accs.map(row).join('')}</tbody></table></div>` : '<p class="vl-note">Пока никто не зарегистрировался.</p>'}</div>
      <div><h4>События</h4><ul class="vl-feed">${(list('События с запуска сервера').length ? list('События с запуска сервера') : ['с запуска сервера событий нет']).map(i => `<li>${esc(i)}</li>`).join('')}</ul>
           <h4>Деплои плагинов</h4><ul class="vl-feed">${list('Последние деплои плагинов').slice(0, 4).map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>
    </div>
    <div class="vl-home-foot"><span>Вход в игре: <code>/register пароль</code> · <code>/login пароль</code> · другим героем: <code>/login Аккаунт пароль</code></span><button class="text-button" data-project="terraria">Паспорт проекта →</button></div>
  </section>`;
}
function home() {
  if (!isHome() || !live) return;
  const grid = document.querySelector('.stats-grid');
  if (!grid) return;
  const old = document.querySelector('[data-vl-home]');
  if (old && old.dataset.at === live.updated) return;
  const html = homeTerraria();
  if (old) old.outerHTML = html; else grid.insertAdjacentHTML('afterend', html);
  const el = document.querySelector('[data-vl-home]'); if (el) el.dataset.at = live.updated;
  const alerts = Object.values(live.projects || {}).flatMap(p => p.alerts || []);
  const card = document.querySelector('.stat-card[data-route="alerts"]');
  if (card) { const s = card.querySelector('strong'), sm = card.querySelector('small'); if (s) s.textContent = alerts.length; if (sm) sm.textContent = alerts.length ? 'живые проверки · есть предупреждения' : 'живые проверки · всё в порядке'; }
}

function inject() {
  const box = document.querySelector('#dialog-content');
  if (!box || !lastId || !box.querySelector('.project-detail-top')) return;
  const old = box.querySelector('[data-vl-panel]') || box.querySelector('.vl-panel');
  if (old && old.dataset.vlPanel === lastId && old.dataset.vlAt === String(loadedAt?.valueOf())) return;
  const html = panel(lastId);
  if (old) old.outerHTML = html;
  else (box.querySelector('.detail-description') || box.querySelector('.project-detail-top')).insertAdjacentHTML('afterend', html);
  const el = box.querySelector('.vl-panel'); if (el) el.dataset.vlAt = String(loadedAt?.valueOf());
  const tag = box.querySelector('.snapshot-tag');
  if (tag && live?.projects?.[lastId]) tag.textContent = fresh() ? 'Живые данные' : 'Данные устарели';
}
function refreshOpen() { if (document.querySelector('#detail')?.open) inject(); }

document.addEventListener('click', ev => {
  const t = ev.target.closest('[data-project],[data-repo]');
  if (t?.dataset.project) lastId = t.dataset.project;
}, true);
new MutationObserver(() => { inject(); }).observe(document.querySelector('#dialog-content') || document.body, { childList: true, subtree: true });
new MutationObserver(() => { if (!document.querySelector('[data-vl-badge]')) badge(); if (isHome() && !document.querySelector('[data-vl-home]')) home(); }).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });

const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = './live.css'; document.head.append(css);
load(); setInterval(load, 60e3);

// ── Главная: «Что требует внимания», «Деньги», «Здоровье серверов» (данные: projects.json → owner) ──
const gb = b => b == null ? '—' : b >= 1e12 ? (b / 1e12).toFixed(1) + ' ТБ' : b >= 1e9 ? (b / 1e9).toFixed(1) + ' ГБ' : (b / 1e6).toFixed(0) + ' МБ';
const rub = v => v == null || v === '' ? '—' : (typeof v === 'number' ? v.toLocaleString('ru', { maximumFractionDigits: 2 }) : esc(v)) + ' ₽';
const usd = v => v == null ? '—' : '$' + Number(v).toLocaleString('ru', { maximumFractionDigits: 2 });
const lvl = (v, warn, bad) => v == null ? '' : v >= bad ? 'vl-bad' : v >= warn ? 'vl-warnc' : 'vl-okc';
const bar = (v, warn = 75, bad = 90) => `<div class="vl-bar ${lvl(v, warn, bad)}"><i style="width:${Math.min(100, v ?? 0)}%"></i></div>`;
const upt = s => !s ? '—' : s >= 86400 ? `${Math.floor(s / 86400)} дн` : `${Math.floor(s / 3600)} ч`;
const agoTs = t => { if (!t) return 'никогда'; const s = Date.now() / 1000 - t; return s < 180 ? 'сейчас' : s < 3600 ? `${Math.floor(s / 60)} мин назад` : s < 172800 ? `${Math.floor(s / 3600)} ч назад` : `${Math.floor(s / 86400)} дн назад`; };
function miniBars(days, fmt) {
  if (!days?.length) return '';
  const max = Math.max(1, ...days.map(d => d[1]));
  return `<div class="vl-mini">${days.map(([d, v]) => `<i title="${esc(d)}: ${esc(fmt(v))}" style="height:${Math.max(3, v / max * 100)}%"></i>`).join('')}</div>`;
}
function homeOwner() {
  const o = live?.owner;
  if (!o) return '';
  if (o.error) return `<section class="vl-home" data-vl-owner><div class="vl-alert">⚠ Сводка не собралась: ${esc(o.error)}</div></section>`;
  const att = o.attention || [], bad = att.filter(a => a.level === 'bad').length;
  const attHtml = att.length ? `<ul class="vl-att">${att.slice(0, 12).map(a => `<li class="vl-att-${esc(a.level)}"><b>${esc(a.title)}</b>${a.detail ? `<span>${esc(a.detail)}</span>` : ''}<em>${esc(a.where)}</em></li>`).join('')}</ul>${att.length > 12 ? `<p class="vl-note">и ещё ${att.length - 12}</p>` : ''}`
    : '<p class="vl-allgood">✓ Всё в порядке — сервисы работают, диски и сертификаты в норме, деплои прошли.</p>';
  const s = o.money?.shopper, ai = o.money?.ai;
  const shop = s ? `<div class="vl-card"><h4>Shopper · ${esc(s.period || 'неделя')}</h4>
      <div class="vl-big">${rub(s.week)}</div><small>за неделю${s.today != null ? ` · сегодня ${rub(s.today)}` : ''}</small>
      ${miniBars((s.days || []).map((v, i) => [s.dates?.[i] || i, v]), rub)}
      <dl class="vl-dl"><dt>Налог к уплате</dt><dd>${rub(s.tax_due)}</dd><dt>Задолженность</dt><dd>${rub(s.tax_debt)}</dd><dt>Доступно к выводу</dt><dd>${rub(s.available)}</dd><dt>В обработке</dt><dd>${rub(s.processing)}</dd></dl>
      <p class="vl-note">Цифры из админки Shopper — меняются там же.</p></div>` : '';
  const aiHtml = ai ? `<div class="vl-card"><h4>Расходы на ИИ (Claude)</h4>
      <div class="vl-big">${usd(ai.today)}</div><small>сегодня · неделя ${usd(ai.week)} · месяц ${usd(ai.month)}</small>
      ${miniBars(ai.days, usd)}
      <dl class="vl-dl">${Object.entries(ai.by_server || {}).map(([k, v]) => `<dt>Сервер ${esc(k)}</dt><dd>${usd(v.month)} · сессий ${esc(v.sessions)}</dd>`).join('')}</dl>
      <p class="vl-note">${esc(ai.source)}</p></div>` : `<div class="vl-card"><h4>Расходы на ИИ</h4><p class="vl-note">Учёт ещё не набрался.</p></div>`;
  const hs = (o.health || []).map(h => `<div class="vl-card vl-srv"><h4>${esc(h.name)}<span class="vl-up">работает ${esc(upt(h.uptime_s))}</span></h4>
      <div class="vl-row"><span>Процессор (${esc(h.cpus)} ядра)</span><b>${esc(h.load ?? '—')}%</b></div>${bar(h.load, 80, 150)}
      <div class="vl-row"><span>Память ${esc(gb(h.ram_total))}</span><b>${esc(h.ram ?? '—')}%</b></div>${bar(h.ram, 80, 92)}
      ${h.swap != null ? `<div class="vl-row"><span>Подкачка</span><b>${esc(h.swap)}%</b></div>${bar(h.swap, 50, 80)}` : ''}
      <div class="vl-row"><span>Диск · свободно ${esc(gb(h.disk_free))}</span><b>${esc(h.disk ?? '—')}%</b></div>${bar(h.disk, 80, 90)}
      <div class="vl-chips"><span>служб ${esc(h.services)}${h.services_down ? ` · <b class="vl-bad-t">не работает ${esc(h.services_down)}</b>` : ''}</span><span>контейнеров ${esc(h.docker)}</span>${h.banned != null ? `<span>заблокировано взломщиков ${esc(h.banned)}</span>` : ''}</div></div>`).join('');
  const keys = o.vpn_keys || [];
  const vpn = keys.length ? `<div class="vl-card"><h4>VPN · ключи<span class="vl-up">онлайн ${keys.filter(k => k.online).length} из ${keys.length}</span></h4>
      <div class="vl-tablewrap"><table class="vl-table"><thead><tr><th>Ключ</th><th>Трафик</th><th>Был в сети</th></tr></thead><tbody>${keys.map(k => `<tr><td>${k.online ? '<i class="vl-dot vl-on"></i>' : '<i class="vl-dot"></i>'}${esc(k.name)}</td><td>${esc(gb(k.rx + k.tx))}</td><td>${esc(k.online ? 'сейчас' : agoTs(k.last))}</td></tr>`).join('')}</tbody></table></div>
      <p class="vl-note">Трафик считается с последнего перезапуска VPN.</p></div>` : '';
  const dep = (o.deploys || []).length ? `<div class="vl-card"><h4>Последние деплои</h4><ul class="vl-feed">${o.deploys.map(d => `<li><b>${esc(d.name)}</b> · ${esc(d.line)}</li>`).join('')}</ul></div>` : '';
  return `<section class="vl-home vl-owner" data-vl-owner>
    <div class="vl-home-head"><div><h2>Что требует внимания</h2><p>Проверяется каждую минуту на обоих серверах</p></div>
      <div class="vl-home-status ${bad ? 'vl-bad' : att.length ? 'vl-warn' : 'vl-ok'}">${bad ? `● Проблем: ${bad}` : att.length ? `● Предупреждений: ${att.length}` : '● Всё хорошо'}<small>обновлено ${esc(hhmm(o.updated))}</small></div></div>
    ${attHtml}
    <h3 class="vl-sec">Деньги</h3><div class="vl-grid">${shop}${aiHtml}</div>
    <h3 class="vl-sec">Здоровье серверов</h3><div class="vl-grid">${hs}${vpn}</div>
    ${dep ? `<div class="vl-grid">${dep}</div>` : ''}
  </section>`;
}
function homeOwnerRender() {
  if (!isHome() || !live) return;
  const grid = document.querySelector('.stats-grid');
  if (!grid) return;
  const old = document.querySelector('[data-vl-owner]');
  if (old && old.dataset.at === live.updated) return;
  const html = homeOwner();
  if (!html) return;
  if (old) old.outerHTML = html; else grid.insertAdjacentHTML('afterend', html);
  const el = document.querySelector('[data-vl-owner]'); if (el) el.dataset.at = live.updated;
}
new MutationObserver(() => { if (isHome() && live && !document.querySelector('[data-vl-owner]')) homeOwnerRender(); }).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });
setInterval(homeOwnerRender, 5000); setTimeout(homeOwnerRender, 800);
