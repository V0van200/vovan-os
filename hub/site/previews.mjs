import {esc,kindLabels} from './model.mjs';
import {icon} from './icons.mjs';

// Public first-screen captures, reviewed on 2026-10-12. No authenticated pages.
export const previews = {
  'eeklera-site': {file:'eeklera.jpg',host:'eeklera.online'},
  'cools1s': {file:'cools1s.jpg',host:'cools1s.ru'},
  'eeklera-os': {file:'eeklera-os.jpg',host:'os.eeklera.online'}
};
export function projectPreview(p,extra='') {
  const shot=previews[p.id];
  if(shot) return `<div class="project-preview ${extra}"><img src="./assets/previews/${shot.file}" alt="Первый экран ${esc(shot.host)}, снимок от 12.10.2026" loading="lazy" width="1265" height="712"><span class="preview-caption">${esc(shot.host)} <span>12.10.2026</span></span></div>`;
  const glyph={game:'game',agents:'brain',bot:'bot',site:'globe',infra:'server'}[p.kind]||'box';
  return `<div class="project-identity ${extra}"><span class="identity-icon">${icon(glyph)}</span><span>${esc(kindLabels[p.kind]||'Проект')}</span><span class="identity-code">${esc(p.id)}</span></div>`;
}
