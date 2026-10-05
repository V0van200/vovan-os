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
  badge(); refreshOpen();
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
new MutationObserver(() => { if (!document.querySelector('[data-vl-badge]')) badge(); }).observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });

const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = './live.css'; document.head.append(css);
load(); setInterval(load, 60e3);
