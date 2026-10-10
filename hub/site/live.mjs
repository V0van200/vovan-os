import { icon } from './icons.mjs';
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

// ── Главная: счётчик проблем в карточке «Предупреждения» ──
const isHome = () => ['', '#', '#home', '#/home'].includes(location.hash);
function home() {
  if (!isHome() || !live) return;
  const alerts = (live.owner?.attention || []).filter(a => a.where !== 'проект');
  const card = document.querySelector('.stat-card[data-route="alerts"]');
  if (card) { const s = card.querySelector('strong'), sm = card.querySelector('small'); if (s) s.textContent = alerts.length; if (sm) sm.textContent = alerts.length ? 'живые проверки · есть проблемы' : 'живые проверки · всё в порядке'; }
  side();
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
new MutationObserver(() => { if (!document.querySelector('[data-vl-badge]')) badge(); if (isHome() && !document.querySelector('[data-vl-side]')) home(); }).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });

const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = './live.css'; document.head.append(css);
load(); setInterval(load, 60e3);


// ── Правая колонка в стиле хаба: «Состояние системы», «Terraria», живой «Последний деплой» ──
const gbs = b => b == null ? '—' : b >= 1e9 ? (b / 1e9).toFixed(1) + ' ГБ' : (b / 1e6).toFixed(0) + ' МБ';
const agoS = t => { if (!t) return 'никогда'; const s = Date.now() / 1000 - t; return s < 180 ? 'сейчас' : s < 3600 ? `${Math.floor(s / 60)} мин` : s < 172800 ? `${Math.floor(s / 3600)} ч` : `${Math.floor(s / 86400)} дн`; };
const open = new Set(JSON.parse(localStorage.getItem('vl-open') || '[]'));
const head = (title, ico, id) => `<div class="panel-heading"><h2>${icon(ico)}${esc(title)}</h2><button class="text-button" data-vl-toggle="${id}" aria-expanded="${open.has(id)}">${open.has(id) ? 'Свернуть' : 'Подробнее'} ${icon('chevron')}</button></div>`;
const meter = (label, v) => `<div class="meter-row"><span class="vl-ml">${esc(label)}</span><div class="meter vl-m${v >= 90 ? 'bad' : v >= 75 ? 'warn' : ''}"><i style="width:${Math.min(100, v ?? 0)}%"></i></div><b>${v == null ? '—' : esc(v) + '%'}</b></div>`;
function sysPanel() {
  const o = live?.owner; if (!o || o.error) return '';
  const att = (o.attention || []).filter(a => a.where !== 'проект'), bad = att.filter(a => a.level === 'bad').length;
  const st = bad ? `<span class="status inactive">Проблем: ${bad}</span>` : att.length ? `<span class="status partial">Внимание: ${att.length}</span>` : '<span class="status active">Всё в порядке</span>';
  const hs = o.health || [], keys = o.vpn_keys || [];
  const brief = hs.map(h => `<div class="vl-srv"><small>${esc(h.name)}</small>${meter('CPU', h.load)}${meter('ОЗУ', h.ram)}${meter('Диск', h.disk)}</div>`).join('');
  const more = open.has('sys') ? `
    ${att.length ? `<div class="commit-list vl-att">${att.map(a => `<button type="button"><i class="vl-${esc(a.level)}"></i><span>${esc(a.title)}<small>${esc(a.detail)}</small></span><b>${esc(a.where)}</b></button>`).join('')}</div>` : ''}
    ${hs.map(h => `<div class="vl-srvx"><small>${esc(h.name)} · работает ${esc(Math.floor((h.uptime_s || 0) / 86400))} дн</small>
      <div class="vl-kv"><span>Подкачка</span><b>${h.swap == null ? 'нет' : esc(h.swap) + '%'}</b><span>Свободно на диске</span><b>${esc(gbs(h.disk_free))}</b><span>Служб</span><b>${esc(h.services)}${h.services_down ? ` · не работает ${esc(h.services_down)}` : ''}</b><span>Заблокировано взломщиков</span><b>${esc(h.banned ?? '—')}</b></div></div>`).join('')}
    ${keys.length ? `<div class="vl-srvx"><small>VPN · онлайн ${keys.filter(k => k.online).length} из ${keys.length}</small><div class="commit-list">${keys.map(k => `<button type="button"><i class="${k.online ? '' : 'vl-off'}"></i><span>${esc(k.name)}<small>${k.online ? 'в сети' : 'был ' + esc(agoS(k.last))}</small></span><b>${esc(gbs(k.rx + k.tx))}</b></button>`).join('')}</div></div>` : ''}` : '';
  return `<section class="panel vl-sys" data-vl-side="sys">${head('Состояние системы', 'shield', 'sys')}<div class="panel-sub">Проверка каждую минуту · ${esc(hhmm(o.updated))}</div><div class="vl-st">${st}</div>${brief}${more}</section>`;
}
function terraPanel() {
  const t = live?.projects?.terraria; if (!t) return '';
  const w = t.world || {}, accs = t.accounts || [], on = t.online_names || [];
  const running = !(t.alerts || []).some(a => a.includes('остановлен'));
  const more = open.has('terra') ? `<div class="commit-list">${accs.map(a => `<button type="button"><i class="${a.online ? '' : 'vl-off'}"></i><span>${esc(a.name)}<small>${esc(a.group)} · ❤ ${esc(a.hp ?? '—')}/${esc(a.max_hp ?? '—')} · смертей ${esc(a.deaths ?? 0)}</small></span><b>${esc(a.online ? 'в игре' : a.last ? new Date(a.last + 'Z').toLocaleDateString('ru', { day: '2-digit', month: '2-digit' }) : '—')}</b></button>`).join('') || '<div class="mini-empty">Аккаунтов пока нет</div>'}</div>
    <div class="vl-kv"><span>Мир</span><b>${esc(w.name || '—')}</b><span>Размер</span><b>${esc(w.size || '—')}</b><span>Адрес</span><b>${esc(w.address || '—')}</b><span>Защита спавна</span><b>${w.spawn_protection ? esc(w.spawn_protection) + ' блоков' : 'нет'}</b></div>` : '';
  return `<section class="panel vl-terra" data-vl-side="terra">${head('Terraria', 'game', 'terra')}<div class="panel-sub">${esc(w.name || 'мир')} · ${esc(w.size || '')}</div>
    <div class="vl-st">${running ? '<span class="status active">Сервер работает</span>' : '<span class="status inactive">Сервер остановлен</span>'}<span class="status live">Онлайн: ${esc(on.length)}</span><span class="status">Аккаунтов: ${esc(accs.length)}</span></div>${more}</section>`;
}
function deployFill() {
  const box = document.querySelector('.deploy-widget'); const d = live?.owner?.deploys;
  if (!box || !d?.length) return;
  const key = JSON.stringify(d); if (box.dataset.vlAt === key) return;
  const h = box.querySelector('.panel-heading')?.outerHTML || '';
  const row = x => { const m = x.line.match(/^(\S+) (\S+) (\S+) (\S+) (.*)$/) || []; const ok = m[3] === 'OK' || m[3] === 'ADOPTED';
    return `<button type="button"><i class="${ok ? '' : 'vl-bad'}"></i><span>${esc(x.name)}<small>${esc((m[5] || x.line).replace(/\s*\((root|Claude|V0van200|[^)]*)\)\s*$/, '').slice(0, 70))}</small></span><b>${esc(m[1] ? m[1].slice(5).split('-').reverse().join('.') + ' ' + (m[2] || '').slice(0, 5) : '')}</b></button>`; };
  box.innerHTML = `${h}<div class="panel-sub">Автодеплой из GitHub · ${d.length} проекта</div><div class="commit-list">${d.map(row).join('')}</div>`;
  box.dataset.vlAt = key;
}
function side() {
  if (!isHome() || !live) return;
  const col = document.querySelector('aside.right-column'); if (!col) return;
  for (const [id, fn] of [['sys', sysPanel], ['terra', terraPanel]]) {
    const html = fn(), old = col.querySelector(`[data-vl-side="${id}"]`);
    if (!html) { old?.remove(); continue; }
    if (old) { if (old.outerHTML !== html) old.outerHTML = html; }
    else if (id === 'sys') col.insertAdjacentHTML('afterbegin', html);
    else col.querySelector('[data-vl-side="sys"]')?.insertAdjacentHTML('afterend', html);
  }
  deployFill();
}
document.addEventListener('click', ev => {
  const b = ev.target.closest('[data-vl-toggle]'); if (!b) return;
  const id = b.dataset.vlToggle; open.has(id) ? open.delete(id) : open.add(id);
  localStorage.setItem('vl-open', JSON.stringify([...open])); side();
});
