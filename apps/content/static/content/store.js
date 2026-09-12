(() => {
  const key = 'gioia-favorites-v1';
  let favorites = new Set();
  try { const stored = JSON.parse(localStorage.getItem(key) || '[]'); if (Array.isArray(stored)) favorites = new Set(stored.filter(value => typeof value === 'string')); } catch (_) {}
  let onlyFavorites = false;
  let timer;
  const cards = [...document.querySelectorAll('[data-product]')];
  const toast = message => {
    const node = document.querySelector('#toast');
    node.textContent = message; node.hidden = false;
    clearTimeout(timer); timer = setTimeout(() => { node.hidden = true; }, 3000);
  };
  const refresh = () => {
    document.querySelector('#favorite-count').textContent = favorites.size;
    document.querySelectorAll('[data-favorite]').forEach(button => {
      const active = favorites.has(button.dataset.favorite);
      button.setAttribute('aria-pressed', String(active));
      button.textContent = button.classList.contains('favorite') ? (active ? '♥' : '♡') : (active ? '♥ Идея сохранена' : '♡ Сохранить идею');
      if (button.classList.contains('favorite')) button.setAttribute('aria-label', active ? 'Удалить из избранного' : 'Добавить в избранное');
    });
    cards.forEach(card => { card.hidden = onlyFavorites && !favorites.has(card.dataset.product); });
    document.querySelector('#favorites-empty').hidden = !onlyFavorites || cards.some(card => !card.hidden);
    document.querySelector('#favorites-toggle').setAttribute('aria-pressed', String(onlyFavorites));
    document.querySelector('#result-count').textContent = onlyFavorites ? `В избранном в этой выборке: ${cards.filter(card => !card.hidden).length}` : `Вариантов: ${cards.length}`;
  };
  document.querySelectorAll('[data-favorite]').forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.favorite;
    if (favorites.has(id)) favorites.delete(id); else favorites.add(id);
    try { localStorage.setItem(key, JSON.stringify([...favorites])); } catch (_) { toast('Сохранение в браузере недоступно. Выбор сохранится до закрытия страницы.'); }
    refresh();
  }));
  document.querySelector('#favorites-toggle').addEventListener('click', () => {
    onlyFavorites = !onlyFavorites; refresh(); document.querySelector('#catalog').scrollIntoView({behavior: 'smooth'});
  });
  document.querySelector('#show-all').addEventListener('click', () => { onlyFavorites = false; refresh(); });
  document.querySelector('#sort-select').addEventListener('change', event => {
    document.querySelector('#filter-form').requestSubmit();
  });
  document.querySelectorAll('[data-open]').forEach(button => button.addEventListener('click', () => {
    document.getElementById(button.dataset.open).showModal();
  }));
  document.querySelectorAll('dialog').forEach(dialog => {
    dialog.querySelector('.close-dialog').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      const rect = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
    });
  });
  refresh();
})();
