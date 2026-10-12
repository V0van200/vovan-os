const badge = () => document.querySelector('[data-hub-connection]');
let source = null, retryTimer = null, state = 'checking';

function show(next) {
  state = next;
  const el = badge();
  if (!el) return;
  const labels = {
    checking: 'ПОДКЛЮЧЕНИЕ…',
    connected: 'ОНЛАЙН · ЖИВОЙ ПОТОК',
    reconnecting: 'ОНЛАЙН · ПЕРЕПОДКЛЮЧЕНИЕ',
    unavailable: 'НЕТ СВЯЗИ С API'
  };
  el.textContent = labels[state] || labels.unavailable;
  el.dataset.connection = state;
  el.title = state === 'connected'
    ? 'Открыт защищённый поток обновлений хаба'
    : 'Статус онлайн-соединения с хабом';
}

async function connect() {
  clearTimeout(retryTimer);
  show('checking');
  try {
    const response = await fetch('./api/health', { cache: 'no-store' });
    if (!response.ok) throw new Error('API unavailable');
    const data = await response.json();
    if (data.ok !== true) throw new Error('API unavailable');
    source?.close();
    source = new EventSource('./api/events');
    source.onopen = () => show('connected');
    source.onerror = () => show('reconnecting');
    source.addEventListener('snapshot', () => {
      document.dispatchEvent(new CustomEvent('hub:live-updated'));
    });
  } catch {
    show('unavailable');
    retryTimer = setTimeout(connect, 15000);
  }
}

new MutationObserver(() => { if (badge()?.dataset.connection !== state) show(state); })
  .observe(document.querySelector('#app') || document.body, { childList: true, subtree: true });
connect();

