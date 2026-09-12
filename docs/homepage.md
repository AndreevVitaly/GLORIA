# Главная страница GIOIA

Маршрут `/` отображает адаптивную страницу знакомства с магазином на Django Templates.
Ориентир структуры каталога: https://rus-buket.ru/cvety — категории, фильтры, сортировка,
сетка фотографий. Дизайн и тексты GIOIA самостоятельные.

Реализованы поиск по названию и составу, совместные фильтры цветов и цены, сортировка,
диалог карточки, избранное в localStorage и его просмотр. Разделы «О GIOIA», «Доставка»
и анонс конструктора доступны через навигацию.

Коллекция в `apps/content/showcase.py` демонстрационная и не является каталогом продаваемых
товаров. Цены ориентировочные, фотографии иллюстративные, приём заказов недоступен — это
обозначено на странице. Подключение товарных моделей, корзины и оформления — отдельная работа.

Основные файлы:

- `apps/content/views.py` — серверный поиск, фильтры, сортировка;
- `apps/content/templates/content/home.html` — страница;
- `apps/content/static/content/store.css` — адаптивный дизайн;
- `apps/content/static/content/store.js` — избранное, диалоги и сортировка;
- `apps/content/static/content/images/` — локальные изображения.

Источники фотографий (Unsplash, иллюстративные материалы):

| Файл | Источник |
|---|---|
| roses.jpg | https://images.unsplash.com/photo-1518895949257-7621c3c786d7 |
| bouquet.jpg | https://images.unsplash.com/photo-1561181286-d3fee7d55364 |
| tulips.jpg | https://images.unsplash.com/photo-1520763185298-1b434c919102 |
| garden.jpg | https://images.unsplash.com/photo-1457089328109-e5d9bd499191 |
| peonies.jpg | https://images.unsplash.com/photo-1563241527-3004b7be0ffd |
| red-roses.jpg | https://images.unsplash.com/photo-1562690868-60bbe7293e94 |

Шрифты Manrope и Prata подключаются через Google Fonts; предусмотрены системные fallback-шрифты.
Фотографии доступны локально, без внешних запросов при открытии страницы.
