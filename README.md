Система аутентификации и авторизации (Django + DRF + JWT + RBAC)
Описание проекта
Проект реализует собственную систему аутентификации и авторизации без использования «из коробки» auth‑возможностей Django/DRF (стандартные login/logout/permissions не используются). Основные особенности:
​

Кастомная модель пользователя с авторизацией по email.

Хранение пароля в виде bcrypt‑хэша.

Аутентификация по JWT‑токену в заголовке Authorization: Bearer <token>.

Собственная RBAC‑система (roles, business_elements, access_role_rules).

API для:

регистрации, логина и логаута;

просмотра/обновления профиля и мягкого удаления пользователя;

управления ролями и правилами доступа (только для роли admin);

доступа к мок‑ресурсам (products, orders) с проверкой прав.
​

Рекомендуемые технологии из ТЗ (DRF + Postgres) использованы через Docker‑окружение.
​

Структура проекта
text
auth_project/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py       # настройки Django/DRF, БД, STATIC_URL, ROOT_URLCONF
│   ├── urls.py           # маршруты API
│   ├── asgi.py
│   └── wsgi.py
└── core/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py         # User, Role, UserRole, BusinessElement, AccessRoleRule
    ├── serializers.py    # Register/Login/Profile + RBAC сериализаторы
    ├── authentication.py # JWTAuthentication
    ├── permissions.py    # IsAuthenticatedCustom, IsAdmin, RbacPermission
    ├── views_auth.py     # RegisterView, LoginView, LogoutView
    ├── views_user.py     # UserProfileView (GET/PUT/PATCH/DELETE)
    ├── views_rbac_admin.py # CRUD для ролей/элементов/правил (admin)
    ├── views_mock.py     # Mock-ресурсы (products, orders)
    ├── utils.py          # generate_jwt, decode_jwt
    ├── migrations/
    │   └── 0001_initial.py
    └── management/
        └── commands/
            └── init_rbac_demo.py  # инициализация ролей/элементов/правил/админа
Схема базы данных и модель авторизации
Пользователь (User)
Таблица core_user:

id (UUID, PK)

first_name

last_name

middle_name (nullable)

email (уникальный логин)

password_hash (bcrypt‑хэш пароля)

is_active (мягкое удаление)

is_staff, is_superuser (для совместимости с админкой)

created_at, updated_at

Особенности:

Логин выполняется по email.

Пароль хранится только в виде bcrypt‑хэша в password_hash.

is_active=False означает, что пользователь не может логиниться (soft delete).

Роли и RBAC
Role (core_role)

id

name (например: admin, user)

description

UserRole (core_userrole)

id

user_id → User

role_id → Role

уникальный (user, role)

BusinessElement (core_businesselement)

id

code (строковый код: "users", "products", "orders", "access_rules")

description

AccessRoleRule (core_accessrolerule)

id

role_id → Role

element_id → BusinessElement

read_permission (чтение своих объектов)

read_all_permission (чтение любых объектов)

create_permission

update_permission (обновление своих объектов)

update_all_permission (обновление любых объектов)

delete_permission (удаление своих объектов)

delete_all_permission (удаление любых объектов)

Семантика:

*_permission — действие только с объектами, владельцем которых является пользователь (по полю owner_id / user_id).

*_all_permission — действие над любыми объектами данного типа (админские полномочия).

Если для метода нет ни одного разрешающего флага — запрос завершается с 403 Forbidden.
​

Тестовые данные (init_rbac_demo)
Команда python manage.py init_rbac_demo создаёт:

роли: admin, user;

элементы: users, products, orders, access_rules;

правила:

admin: полный доступ ко всем элементам (все флаги True);

user:

products: read_all_permission=True (видит все товары);

orders: read_permission=True, create_permission=True, update_permission=True, delete_permission=True (работа только со своими заказами);

администратора:

email: admin@example.com

пароль: adminpass

роль: admin.

Аутентификация
Хранение пароля
Пароль никогда не хранится в чистом виде:

при регистрации он хэшируется с помощью bcrypt и сохраняется в поле password_hash;

при логине введённый пароль сравнивается с хэшем из БД.
​

JWT‑токен
Используется библиотека PyJWT:

при успешном логине генерируется access‑токен с payload:

sub: user.id

iat: время выпуска

exp: время жизни токена (по умолчанию 1 час)

токен передаётся клиенту и далее используется в заголовке:

text
Authorization: Bearer <access_token>
Кастомный класс аутентификации
core.authentication.JWTAuthentication:

читает заголовок Authorization;

выделяет токен, декодирует его;

по sub находит пользователя;

проверяет:

существование пользователя;

is_active=True;

если всё ок — устанавливает request.user и возвращает (user, token);

при ошибках токена или неактивном пользователе возбуждает AuthenticationFailed, что приводит к 401 Unauthorized.

Таким образом выполняется требование ТЗ: “После login система при последующих обращениях должна идентифицировать пользователя”.
​

Авторизация (RBAC)
Основная идея
Каждый view, к которому применяются ограничения, содержит поле element_code (например "products").

Общий permission‑класс RbacPermission:

определяет элемент по element_code;

находит все роли пользователя;

по ролям подгружает записи AccessRoleRule для этого элемента;

по HTTP‑методу и флагам прав решает, разрешён ли запрос.

Связь HTTP‑метода и флагов
GET, HEAD, OPTIONS:

read_all_permission → чтение любых объектов;

read_permission → чтение только своих объектов (при проверке объекта).

POST:

create_permission → создание объектов.

PUT, PATCH:

update_all_permission → обновление любых объектов;

update_permission → обновление только своих объектов (по owner).

DELETE:

delete_all_permission → удаление любых объектов;

delete_permission → удаление только своих объектов.

Коды ошибок
Если пользователь не аутентифицирован (нет или неверный токен) — 401 Unauthorized (класс аутентификации / IsAuthenticatedCustom).

Если пользователь аутентифицирован, но подходящего правила нет или оно не даёт нужных прав — 403 Forbidden (класс RbacPermission).
​

Административный доступ к правилам
Только пользователи с ролью admin (проверка через IsAdmin) могут использовать эндпоинты:

/api/admin/roles/ — управление ролями;

/api/admin/elements/ — управление бизнес‑элементами;

/api/admin/rules/ — управление правилами доступа.

Функционал пользователя
Регистрация
Endpoint: POST /api/auth/register/

Тело запроса:

json
{
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "middle_name": "Ivanovich",
  "email": "ivan@example.com",
  "password": "userpass",
  "password_confirm": "userpass"
}
Проверки и поведение:

пароли должны совпадать;

email уникальный;

пароль хэшируется через bcrypt, сохраняется в password_hash;

пользователю автоматически назначается роль user;

ответ 201 Created с данными профиля без пароля.

Login
Endpoint: POST /api/auth/login/

Тело запроса:

json
{
  "email": "ivan@example.com",
  "password": "userpass"
}
Поведение:

поиск пользователя по email;

проверка is_active=True;

сравнение пароля с bcrypt‑хэшем;

при успехе формируется JWT и возвращается:

json
{
  "access_token": "<JWT>"
}
При недействительных данных или неактивном пользователе — 400 Bad Request.

Logout
Endpoint: POST /api/auth/logout/

Требует авторизации (валидный JWT).

В stateless JWT‑схеме сервер просто отвечает 204 No Content, а клиент удаляет токен; при необходимости можно реализовать blacklist токенов или хранение сессий, но в рамках ТЗ достаточно самого факта выхода.
​

Профиль
Endpoint: GET /api/user/profile/

Только для аутентифицированных.

Возвращает данные текущего пользователя.

Endpoint: PUT /api/user/profile/ / PATCH /api/user/profile/

Обновляет данные профиля (имя, фамилия, отчество, email с проверкой уникальности).

Мягкое удаление аккаунта
Endpoint: DELETE /api/user/profile/

Устанавливает is_active=False для текущего пользователя.

Возвращает 204 No Content.

После этого:

логин с его email/паролем невозможен (ошибка);

при попытке аутентификации по старому токену пользователь будет считаться неактивным.

Мок‑объекты бизнес‑логики
ТЗ разрешает не создавать реальные таблицы, а использовать mock‑view для демонстрации работы системы.
​

ProductsMockView
Endpoint: GET /api/products/

Использует element_code="products" и permissions [IsAuthenticatedCustom, RbacPermission].

Возвращает захардкоженный список товаров.

401 — без токена.

403 — при отсутствии подходящих RBAC‑прав.

200 — при наличии права read_all_permission или read_permission (для своих объектов).

OrdersMockView
Endpoints:

GET /api/orders/ — чтение списка заказов (mock).

POST /api/orders/ — создание заказа (mock).

Использует element_code="orders" и те же permissions.

Список заказов содержит записи с user_id, что демонстрирует идею проверки owner:

для роли user права настроены так, чтобы он мог работать только со своими заказами (флаги без _all_permission);

для роли admin — полные права (все флаги True).

API‑эндпоинты
Аутентификация и профиль
POST /api/auth/register/ — регистрация.

POST /api/auth/login/ — вход, выдача JWT.

POST /api/auth/logout/ — выход (stateless).

GET /api/user/profile/ — получить профиль текущего пользователя.

PUT /api/user/profile/ — полное обновление профиля.

PATCH /api/user/profile/ — частичное обновление профиля.

DELETE /api/user/profile/ — мягкое удаление (is_active=False).

RBAC (только admin)
GET/POST/PUT/DELETE /api/admin/roles/ — управление ролями.

GET/POST/PUT/DELETE /api/admin/elements/ — управление бизнес‑элементами.

GET/POST/PUT/DELETE /api/admin/rules/ — управление правилами доступа.

Мок‑ресурсы
GET /api/products/ — список товаров (mock).

GET/POST /api/orders/ — список/создание заказов (mock).

Все защищённые эндпоинты требуют заголовок:

text
Authorization: Bearer <access_token>
Установка и запуск
Локально (SQLite)
Клонировать проект и перейти в каталог:

bash
git clone <repo_url> auth_project
cd auth_project
Создать и активировать виртуальное окружение:

bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Установить зависимости:

bash
pip install -r requirements.txt
В config/settings.py убедиться, что DJANGO_DB по умолчанию использует SQLite (как настраивается в файле).

Применить миграции и инициализировать демо‑данные:

bash
python manage.py migrate
python manage.py init_rbac_demo
Запустить сервер:

bash
python manage.py runserver
Сервер доступен по адресу http://127.0.0.1:8000/.

Через Docker (Postgres)
Создать .env в корне:

text
DJANGO_SECRET_KEY=dev-secret-key
DJANGO_DB=postgresql

POSTGRES_HOST=db
POSTGRES_NAME=auth_db
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=auth_password
POSTGRES_PORT=5432
Запустить:

bash
docker-compose up --build
Compose:

поднимет Postgres;

выполнит python manage.py migrate;

выполнит python manage.py init_rbac_demo;

запустит runserver на 0.0.0.0:8000.

Тестовые сценарии (проверка соответствия ТЗ)
Регистрация пользователя → POST /api/auth/register/ → 201.

Login → POST /api/auth/login/ → получение access_token.

Получение профиля → GET /api/user/profile/ с токеном → 200.

Обновление профиля → PATCH /api/user/profile/ → 200.

Мягкое удаление → DELETE /api/user/profile/ → 204, is_active=False.

Повторный логин удалённого пользователя → 400 (ошибка).

Доступ к /api/products/ без токена → 401.

Доступ к /api/admin/rules/ как обычный user → 403.

Доступ к /api/admin/rules/ как admin → 200, работа с RBAC‑правилами.

Работа с /api/orders/:

как обычный пользователь — только в рамках своих прав;

как админ — без ограничений (по настроенным флагам).