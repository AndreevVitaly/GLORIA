# Проект: GIOIA

Необходимо создать полноценный интернет-магазин цветов **GIOIA** на Python/Django с PostgreSQL.

Ключевая особенность проекта — интерактивный **конструктор букета**, в котором пользователь не выбирает готовую фотографию, а самостоятельно формирует состав букета. На экране при изменении состава должен динамически строиться графический 2D-эскиз букета.

Работать итерационно. Не пытаться реализовать весь проект одним большим коммитом. После каждого этапа приложение должно оставаться запускаемым и тестируемым.

---

# 1. Основная концепция

GIOIA — интернет-магазин цветов с двумя основными способами покупки:

1. выбор готового букета из каталога;
2. самостоятельное создание букета через интерактивный конструктор.

Конструктор должен стать одной из центральных функций проекта.

Пользователь выбирает:

* вид цветка;
* сорт при наличии;
* цвет;
* количество;
* зелень;
* дополнительные элементы;
* упаковку;
* ленту;
* открытку;
* дополнительные товары.

По мере изменения параметров система должна автоматически формировать графический эскиз букета.

Не использовать для основного конструктора заранее подготовленные фотографии готовых букетов.

Основной вариант визуализации первой версии:

**SVG / HTML Canvas + JavaScript.**

Каждый вид цветка должен иметь собственное графическое представление и параметры размещения.

Система должна автоматически определять положение элементов композиции.

Пример:

* крупные цветы — ближе к композиционному центру;
* основные цветы — центральная и средняя область;
* небольшие цветы — заполнение промежутков;
* зелень — периферия и внешний контур;
* упаковка — нижний слой;
* декоративные элементы — по заданным правилам.

При изменении состава букета изображение должно перестраиваться.

Добавить действие:

**«Пересобрать композицию»**

При одинаковом составе оно должно создавать другой допустимый вариант расположения элементов, не меняя состав и стоимость.

---

# 2. Технологический стек

Backend:

* Python;
* Django;
* Django REST Framework — предусмотреть возможность использования API;
* PostgreSQL.

Frontend первой версии:

* Django Templates;
* HTML;
* CSS;
* JavaScript;
* SVG или Canvas для конструктора.

Не использовать React на первом этапе без явной необходимости.

Архитектура должна позволять позже создать отдельный frontend или мобильное приложение через API.

---

# 3. Типы пользователей

В системе должны существовать минимум четыре уровня доступа.

## 3.1. Гость

Может:

* просматривать каталог;
* просматривать карточки товаров;
* использовать конструктор букета;
* рассчитывать стоимость;
* добавлять товары и созданные букеты в корзину;
* начать оформление заказа;
* зарегистрироваться или войти.

---

## 3.2. Покупатель

Зарегистрированный пользователь.

Роль:

`customer`

Имеет личный кабинет.

Может:

* редактировать имя;
* телефон;
* email;
* адреса доставки;
* просматривать историю заказов;
* открывать конкретный заказ;
* видеть текущий статус;
* повторять заказ;
* сохранять созданные букеты;
* добавлять букеты в избранное;
* хранить несколько адресов;
* сохранять получателей;
* сохранять тексты открыток;
* менять пароль;
* управлять своими персональными данными.

---

## 3.3. Оператор / продавец

Роль:

`operator`

Это сотрудник магазина.

Должен иметь отдельный рабочий интерфейс.

Может:

* видеть новые заказы;
* открывать заказ;
* подтверждать заказ;
* связываться с клиентом;
* изменять статус заказа;
* назначать время изготовления;
* назначать время доставки;
* видеть состав созданного клиентом букета;
* видеть графическую схему букета;
* видеть комментарии клиента;
* добавлять внутренние комментарии;
* фиксировать оплату;
* отмечать заказ собранным;
* передавать заказ курьеру;
* отменять заказ в рамках своих полномочий.

Оператор не должен иметь полный доступ к системным настройкам магазина.

---

## 3.4. Администратор / руководитель магазина

Роль:

`admin`

Имеет полный управленческий доступ.

Может:

* управлять пользователями;
* управлять операторами;
* создавать сотрудников;
* блокировать сотрудников;
* назначать роли;
* управлять каталогом;
* создавать и редактировать товары;
* управлять видами цветов;
* управлять сортами;
* управлять цветами;
* управлять остатками;
* менять цены;
* управлять упаковками;
* управлять дополнениями;
* управлять зонами доставки;
* управлять стоимостью доставки;
* видеть все заказы;
* видеть статистику;
* просматривать продажи;
* видеть популярные товары;
* видеть популярные цветы;
* видеть популярные пользовательские букеты;
* управлять скидками;
* управлять промокодами;
* управлять контентом сайта;
* управлять настройками магазина.

---

# 4. Авторизация

Использовать собственную пользовательскую модель Django:

`User`

на базе:

`AbstractUser`

Авторизация должна поддерживать:

* email;
* пароль;
* телефон;
* восстановление пароля.

Роль не хранить строкой непосредственно в логике приложения.

Создать нормальную систему ролей и разрешений.

---

# 5. Django-приложения

Предлагаемая структура:

```text
gioia/
    config/

    apps/
        accounts/
        catalog/
        bouquet_builder/
        cart/
        orders/
        payments/
        delivery/
        inventory/
        promotions/
        operator_panel/
        dashboard/
        content/
        notifications/
        core/
```

Назначение:

`accounts`
— пользователи, роли, профили, адреса.

`catalog`
— каталог готовых товаров и компонентов.

`bouquet_builder`
— конструктор букета.

`cart`
— корзина.

`orders`
— заказы.

`payments`
— платежи.

`delivery`
— доставка.

`inventory`
— склад и остатки.

`promotions`
— скидки и промокоды.

`operator_panel`
— рабочее место продавца.

`dashboard`
— интерфейс руководителя магазина.

`content`
— страницы, баннеры и содержимое сайта.

`notifications`
— email/SMS/внутренние уведомления.

`core`
— общие классы, справочники, базовые модели.

---

# 6. PostgreSQL — схема данных

Использовать понятные английские названия таблиц.

Для Django явно задавать `db_table`, чтобы структура PostgreSQL оставалась стабильной и читаемой.

---

# 7. Пользователи

## `users`

Поля:

```text
id
uuid
email
phone
username
password
first_name
last_name
is_active
is_staff
is_superuser
date_joined
last_login
created_at
updated_at
```

---

## `roles`

```text
id
code
name
description
created_at
```

Примеры:

```text
customer
operator
admin
```

---

## `user_roles`

```text
id
user_id
role_id
created_at
```

Позволить одному пользователю при необходимости иметь несколько ролей.

---

## `customer_profiles`

```text
id
user_id
birth_date
marketing_consent
notes
created_at
updated_at
```

---

## `customer_addresses`

```text
id
user_id
title
recipient_name
recipient_phone
city
street
house
building
apartment
entrance
floor
intercom
postal_code
latitude
longitude
delivery_comment
is_default
created_at
updated_at
```

---

## `customer_recipients`

Для сохранённых получателей цветов.

```text
id
user_id
name
phone
relationship
notes
created_at
updated_at
```

---

# 8. Каталог

## `product_categories`

Например:

```text
Букеты
Монобукеты
Композиции
Розы
Подарки
Открытки
```

Поля:

```text
id
parent_id
name
slug
description
is_active
sort_order
created_at
updated_at
```

---

## `products`

Готовые товары.

```text
id
uuid
category_id
name
slug
short_description
description
sku
price
old_price
is_active
is_featured
is_customizable
created_at
updated_at
```

---

## `product_images`

```text
id
product_id
image
alt_text
sort_order
is_primary
created_at
```

---

# 9. Цветы

Создать отдельную предметную модель цветов.

## `flower_types`

Например:

```text
Роза
Пион
Тюльпан
Гербера
Хризантема
Лилия
Гортензия
```

Поля:

```text
id
name
slug
description
default_layer
default_scale
is_active
created_at
updated_at
```

---

## `flower_varieties`

Например разновидности роз.

```text
id
flower_type_id
name
description
is_active
created_at
updated_at
```

---

## `flower_colors`

```text
id
name
hex_color
slug
is_active
created_at
```

---

## `flower_variants`

Конкретная продаваемая разновидность.

Например:

```text
Роза / Red Naomi / красная / 60 см
```

Поля:

```text
id
flower_type_id
flower_variety_id
flower_color_id
sku
stem_length_cm
purchase_price
retail_price
is_active
created_at
updated_at
```

---

# 10. Зелень

## `greenery_types`

```text
id
name
slug
description
retail_price
is_active
created_at
updated_at
```

Примеры:

```text
Эвкалипт
Рускус
Фисташка
Папоротник
```

---

# 11. Упаковка

## `packaging_types`

```text
id
name
slug
description
price
is_active
created_at
updated_at
```

---

## `packaging_colors`

```text
id
packaging_type_id
name
hex_color
is_active
created_at
```

---

## `ribbon_types`

```text
id
name
price
is_active
created_at
updated_at
```

---

# 12. Дополнения

## `addons`

Например:

```text
Открытка
Мягкая игрушка
Конфеты
Ваза
Топпер
```

Поля:

```text
id
name
slug
description
price
stock_quantity
is_active
created_at
updated_at
```

---

# 13. Конструктор букета

Это отдельная центральная сущность.

## `custom_bouquets`

```text
id
uuid
user_id
name
status
composition_seed
subtotal
packaging_price
addons_price
total_price
preview_svg
preview_data
created_at
updated_at
```

`composition_seed` нужен для воспроизводимого расположения элементов.

Одинаковый seed + одинаковый состав должны создавать одинаковый эскиз.

---

## `custom_bouquet_flowers`

```text
id
custom_bouquet_id
flower_variant_id
quantity
unit_price
created_at
```

---

## `custom_bouquet_greenery`

```text
id
custom_bouquet_id
greenery_type_id
quantity
unit_price
created_at
```

---

## `custom_bouquet_packaging`

```text
id
custom_bouquet_id
packaging_type_id
packaging_color_id
ribbon_type_id
price
created_at
```

---

## `custom_bouquet_addons`

```text
id
custom_bouquet_id
addon_id
quantity
unit_price
created_at
```

---

# 14. Графическая библиотека конструктора

Для каждого элемента конструктора необходимо хранить параметры визуализации.

## `bouquet_assets`

```text
id
asset_type
object_id
name
svg_file
width
height
anchor_x
anchor_y
default_rotation
min_rotation
max_rotation
default_scale
min_scale
max_scale
z_index
is_active
created_at
updated_at
```

`asset_type`:

```text
flower
greenery
packaging
decoration
```

---

# 15. Правила композиции

## `bouquet_composition_rules`

```text
id
object_type
object_id
preferred_zone
min_radius
max_radius
min_angle
max_angle
min_scale
max_scale
collision_radius
priority
created_at
updated_at
```

Зоны:

```text
center
middle
outer
edge
background
foreground
```

---

# 16. Алгоритм построения букета

Создать отдельный сервис:

```text
bouquet_builder/services/composer.py
```

Основной класс:

```python
BouquetComposer
```

На вход получает:

```python
flowers
greenery
packaging
seed
canvas_width
canvas_height
```

На выход:

```python
BouquetComposition
```

с координатами:

```text
asset
x
y
scale
rotation
z_index
```

Алгоритм должен:

1. определить центр композиции;
2. разместить крупные цветы;
3. разместить основные цветы;
4. заполнить промежутки;
5. разместить зелень;
6. выполнить проверку коллизий;
7. добавить упаковку;
8. сформировать SVG;
9. вернуть JSON описания композиции.

---

# 17. Пересборка букета

При кнопке:

`Пересобрать`

создавать новый:

`composition_seed`

После чего композиция перестраивается.

Состав и стоимость при этом не меняются.

---

# 18. Сохранение графического результата

Хранить одновременно:

```text
preview_svg
preview_data
```

`preview_data` — JSON.

Пример:

```json
{
  "seed": 18452,
  "elements": [
    {
      "type": "flower",
      "variant_id": 15,
      "x": 412,
      "y": 215,
      "rotation": -8,
      "scale": 1.1,
      "z": 14
    }
  ]
}
```

Это позволит в любой момент воспроизвести букет.

---

# 19. Корзина

## `carts`

```text
id
uuid
user_id
session_key
created_at
updated_at
```

---

## `cart_items`

```text
id
cart_id
product_id
custom_bouquet_id
quantity
unit_price
created_at
updated_at
```

Одна позиция должна ссылаться либо на обычный товар, либо на пользовательский букет.

---

# 20. Заказы

## `orders`

```text
id
uuid
order_number
user_id
status
operator_id
recipient_name
recipient_phone
customer_phone
customer_email
delivery_address_id
delivery_date
delivery_time_from
delivery_time_to
delivery_comment
card_text
subtotal
discount_amount
delivery_price
total_amount
payment_status
created_at
updated_at
```

---

# 21. Статусы заказа

## `order_statuses`

Примеры:

```text
new
confirmed
paid
assembling
assembled
ready_for_delivery
out_for_delivery
delivered
completed
cancelled
```

Поля:

```text
id
code
name
sort_order
is_final
```

---

## `order_status_history`

```text
id
order_id
status_id
changed_by_id
comment
created_at
```

История статусов никогда не должна перезаписываться.

---

# 22. Позиции заказа

## `order_items`

```text
id
order_id
product_id
custom_bouquet_id
name
sku
quantity
unit_price
total_price
snapshot_data
created_at
```

Очень важно:

заказ должен хранить snapshot товара или букета на момент покупки.

Изменение цены или состава каталога впоследствии не должно менять старые заказы.

---

# 23. Комментарии оператора

## `order_notes`

```text
id
order_id
user_id
note
is_internal
created_at
```

---

# 24. Оплата

## `payments`

```text
id
uuid
order_id
provider
external_id
amount
currency
status
payment_method
paid_at
created_at
updated_at
```

---

# 25. Доставка

## `delivery_zones`

```text
id
name
description
base_price
free_delivery_from
is_active
created_at
updated_at
```

---

## `delivery_slots`

```text
id
date
time_from
time_to
capacity
reserved_count
is_active
```

---

# 26. Склад

## `inventory_items`

```text
id
flower_variant_id
greenery_type_id
addon_id
quantity_available
quantity_reserved
updated_at
```

---

## `inventory_transactions`

```text
id
inventory_item_id
transaction_type
quantity
order_id
user_id
comment
created_at
```

Типы:

```text
receipt
reserve
release
sale
writeoff
correction
```

---

# 27. Промокоды

## `promo_codes`

```text
id
code
description
discount_type
discount_value
minimum_order_amount
starts_at
ends_at
usage_limit
usage_count
is_active
created_at
updated_at
```

---

## `promo_code_usages`

```text
id
promo_code_id
user_id
order_id
used_at
```

---

# 28. Избранное

## `favorites`

```text
id
user_id
product_id
custom_bouquet_id
created_at
```

---

# 29. Уведомления

## `notifications`

```text
id
user_id
type
title
message
is_read
created_at
```

---

# 30. Аудит действий сотрудников

Обязательно добавить:

## `audit_log`

```text
id
user_id
action
entity_type
entity_id
old_data
new_data
ip_address
created_at
```

Изменения операторов и администраторов должны быть отслеживаемыми.

---

# 31. Рабочее место оператора

Создать отдельный интерфейс:

```text
/operator/
```

Главный экран:

```text
Новые
Подтвержденные
В работе
Собраны
На доставке
Завершенные
Отмененные
```

В карточке заказа оператор видит:

* номер;
* клиента;
* получателя;
* телефон;
* адрес;
* дату доставки;
* время;
* оплату;
* состав заказа;
* графический эскиз букета;
* подробную спецификацию цветов;
* упаковку;
* дополнения;
* открытку;
* комментарий;
* историю заказа.

---

# 32. Панель руководителя

Отдельный раздел:

```text
/management/
```

Разделы:

```text
Dashboard
Заказы
Каталог
Цветы
Склад
Пользователи
Сотрудники
Доставка
Промокоды
Продажи
Настройки
```

Dashboard должен в дальнейшем показывать:

```text
заказы сегодня
выручку сегодня
средний чек
новые заказы
продажи за неделю
популярные букеты
популярные цветы
остатки
товары с низким остатком
```

---

# 33. Пользовательский интерфейс магазина

Основное меню:

```text
GIOIA

Главная
Каталог
Создать букет
Доставка
О нас
Контакты

Поиск
Избранное
Личный кабинет
Корзина
```

---

# 34. Главная страница

Основной блок:

```text
GIOIA

Цветы, которые дарят радость

[Выбрать букет]
[Создать свой]
```

Ниже:

```text
Популярные букеты

Создай свой букет

Новые поступления

Почему GIOIA

Доставка

Отзывы
```

---

# 35. Страница конструктора

Предлагаемый интерфейс desktop:

```text
---------------------------------------------------

КАТАЛОГ            БУКЕТ            СОСТАВ

Розы                 🌸              Роза × 7
Пионы               🌹🌸            Пион × 3
Тюльпаны           🌿🌹🌿            Эвкалипт × 2
Зелень               ╲╱
Упаковка             ╲╱

[-] 7 [+]

Цвет:
● ● ● ●

                  4 850 ₽

          [Пересобрать]

          [Добавить в корзину]

---------------------------------------------------
```

На мобильном экране:

1. визуализация букета;
2. стоимость;
3. вкладки:

```text
Цветы
Зелень
Упаковка
Дополнения
```

---

# 36. Стоимость букета

Цена всегда рассчитывается сервером.

Frontend может показывать предварительный расчёт, но окончательная стоимость должна пересчитываться backend.

Формула:

```text
цветы
+ зелень
+ упаковка
+ лента
+ дополнительные товары
= стоимость букета
```

Никогда не доверять цене, переданной клиентским JavaScript.

---

# 37. Безопасность

Обязательно:

* CSRF;
* защита доступа по ролям;
* проверка ownership пользовательских объектов;
* серверная валидация;
* защита административных URL;
* логирование действий сотрудников;
* безопасное хранение паролей через Django;
* ограничения загрузки файлов;
* проверка MIME типов;
* защита от изменения стоимости с frontend.

---

# 38. API

Даже если первая версия использует Django Templates, предусмотреть API:

```text
/api/v1/
```

Пример:

```text
/api/v1/catalog/
/api/v1/flowers/
/api/v1/bouquets/
/api/v1/bouquets/compose/
/api/v1/cart/
/api/v1/orders/
/api/v1/profile/
```

---

# 39. Тесты

Использовать pytest.

Создать тесты минимум для:

* регистрации;
* авторизации;
* ролей;
* доступа оператора;
* доступа администратора;
* каталога;
* расчёта стоимости букета;
* сохранения букета;
* воспроизводимости композиции по seed;
* пересборки;
* корзины;
* создания заказа;
* snapshot заказа;
* смены статуса;
* истории статусов;
* складского резерва;
* промокодов.

---

# 40. Первый этап разработки

Начать НЕ со всего интерфейса.

Сначала создать фундамент.

Этап 1:

1. Django-проект.
2. PostgreSQL.
3. структура `apps/`.
4. custom User.
5. Role.
6. UserRole.
7. CustomerProfile.
8. CustomerAddress.
9. FlowerType.
10. FlowerVariety.
11. FlowerColor.
12. FlowerVariant.
13. GreeneryType.
14. PackagingType.
15. CustomBouquet.
16. CustomBouquetFlower.
17. CustomBouquetGreenery.
18. миграции.
19. Django Admin.
20. базовые тесты моделей.

После выполнения:

* показать структуру проекта;
* показать созданные модели;
* показать миграции;
* запустить тесты;
* исправить ошибки;
* не переходить самостоятельно к следующему большому этапу.

---

# 41. Второй этап

После успешного первого этапа реализовать:

**BouquetComposer v0.1**

Пока без красивой графики.

Сделать алгоритм координат:

```text
flower_id
x
y
scale
rotation
z_index
```

И JSON-результат композиции.

Для заданного seed результат должен быть полностью воспроизводимым.

---

# 42. Третий этап

Добавить SVG-рендер.

Сначала использовать простые временные SVG-заглушки:

```text
rose.svg
peony.svg
tulip.svg
eucalyptus.svg
```

Главная задача — проверить механизм композиции.

Не тратить время на художественное качество графики на этом этапе.

---

# 43. Принцип разработки

Приоритет:

```text
архитектура
→ корректная модель данных
→ бизнес-логика
→ тесты
→ API
→ интерфейс
→ графический дизайн
```

Не смешивать бизнес-логику с views и templates.

Использовать services для:

```text
создания заказа
расчёта стоимости
резервирования склада
построения букета
применения скидок
изменения статусов
```

---

# 44. Важный принцип GIOIA

Конструктор — не декоративная функция.

Созданный клиентом букет должен существовать как полноценный объект системы.

Цепочка:

```text
CustomBouquet
        ↓
Composition
        ↓
CartItem
        ↓
OrderItem
        ↓
оператор
        ↓
флорист
        ↓
готовый физический букет
```

Графическая композиция и список компонентов должны сохраняться вместе с заказом.

Даже если пользователь позже изменит или удалит свой сохранённый букет, заказ должен содержать неизменяемый snapshot того варианта, который был приобретён.

---

# Итог

Создать фундамент проекта GIOIA как промышленно структурированного интернет-магазина, а не демонстрационной страницы.

Главные сущности первой версии:

```text
User
Role
Customer
Product
Flower
FlowerVariant
Greenery
Packaging
CustomBouquet
BouquetComposition
Cart
Order
Payment
Delivery
Inventory
Promotion
```

Главная уникальная функция продукта:

**пользователь самостоятельно выбирает состав букета, а система в реальном времени формирует графическое изображение именно его композиции, автоматически рассчитывает стоимость и сохраняет точную спецификацию для последующей сборки сотрудником магазина.**
