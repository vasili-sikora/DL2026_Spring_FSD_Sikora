# Проектирование и анализ

## 1.1. Пользовательские сценарии (User Story)

1. Как пользователь, я хочу выбрать шаблон, ввести верхний и нижний текст, настроить шрифт, размер и цвет, чтобы быстро сгенерировать мем и сохранить его в своем профиле.
2. Как пользователь, я хочу видеть список своих сгенерированных изображений и открывать каждое по `id`, чтобы управлять результатами генерации.
3. Как администратор, я хочу загружать новые шаблоны и настраивать зоны текста (координаты и ширину блоков), чтобы новые шаблоны корректно работали для всех пользователей.

## 1.2. Функциональные требования

### Обязательные

Frontend:
- Регистрация, вход и выход пользователя.
- Каталог шаблонов и просмотр изображения шаблона.
- Форма генерации: `text_top`, `text_bottom`, `font_name`, `font_size`, `font_color`.
- Preview перед генерацией.
- Страница с личными сгенерированными изображениями.
- Админ-страница для загрузки шаблонов и разметки текстовых зон.

Backend:
- Session-cookie авторизация (`/auth/*`) с получением текущего пользователя через dependency.
- CRUD-операции, необходимые для:
  - чтения шаблонов;
  - генерации и чтения пользовательских изображений;
  - админских операций по шаблонам.
- Валидация входных данных (формат email, пароль, формат изображения, границы layout).
- Ограничение частоты запросов на preview/generate.
- Хранение данных в SQLite.

### Опциональные

- Drag-and-drop редактор текстовых зон в админке (вместо числовых полей).
- Дополнительные стили текста (обводка, тень, пресеты контраста).
- Пагинация/фильтрация списка сгенерированных изображений.

## 1.3. Проектирование API

Ниже приведен целевой API.

### Аутентификация

- `POST /auth/register`
  - Body: `{ "email": "string", "password": "string" }`
  - Response `200`: `{ "id": number, "email": "string", "is_admin": 0|1 }`
  - Устанавливает session cookie.

- `POST /auth/login`
  - Body: `{ "email": "string", "password": "string" }`
  - Response `200`: `{ "id": number, "email": "string", "is_admin": 0|1 }`
  - Устанавливает session cookie.

- `POST /auth/logout`
  - Response `200`: `{ "detail": "Logged out" }`
  - Очищает session cookie.

- `GET /auth/me` (требует авторизацию)
  - Response `200`: `{ "id": number, "email": "string", "is_admin": 0|1 }`

### Шаблоны

- `GET /templates`
  - Response `200`: `Template[]`

- `GET /templates/{template_id}`
  - Response `200`: `Template`
  - Response `404`: `{ "detail": "Template not found" }`

- `GET /templates/{template_id}/image`
  - Response `200`: файл изображения шаблона
  - Response `404`: template или file not found

- `POST /templates` (admin-only)
  - Body: `{ "name": "string", "image_name": "string" }`
  - Response `200`: `Template`

- `POST /admin/templates/upload` (admin-only)
  - `multipart/form-data`:
    - `name: string`
    - `image: file(.jpg|.jpeg|.png)`
  - Response `200`: `Template`

- `PATCH /admin/templates/{template_id}/layout` (admin-only)
  - Body:
    - `top_text_x`, `top_text_y`, `top_text_width`
    - `bottom_text_x`, `bottom_text_y`, `bottom_text_width`
  - Response `200`: обновленный `Template`

- `POST /admin/templates/{template_id}/layout-preview` (admin-only)
  - Body:
    - layout-поля как выше
    - `sample_text_top`, `sample_text_bottom`
    - `font_name`, `font_size`, `font_color`
  - Response `200`: preview JPEG

### Генерация изображений

- `GET /generated_images` (требует авторизацию)
  - Response `200`: список изображений текущего пользователя

- `GET /generated_images/{image_id}` (требует авторизацию)
  - Response `200`: одно изображение текущего пользователя
  - Response `404`: `{ "detail": "Image not found" }`

- `POST /templates/{template_id}/preview`
  - Body:
    - `text_top`, `text_bottom`
    - `font_name`, `font_size`, `font_color`
  - Response `200`: preview JPEG

- `POST /templates/{template_id}/generate` (требует авторизацию)
  - Body:
    - `text_top`, `text_bottom`
    - `font_name`, `font_size`, `font_color`
  - Response `200`: созданная запись изображения

- `GET /images/{share_token}`
  - Публичный доступ к изображению по share token
  - Response `200`: файл изображения

## 1.4. Модель данных

Основные сущности:

### `users`

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Идентификатор пользователя |
| `email` | TEXT UNIQUE | Email пользователя |
| `password` | TEXT | Хэш пароля |
| `is_admin` | INTEGER DEFAULT 0 | Флаг администратора (0/1) |

### `templates`

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Идентификатор шаблона |
| `name` | TEXT | Название шаблона |
| `image_path` | TEXT | Относительный путь к изображению шаблона |
| `top_text_x` | INTEGER \| NULL | X-координата верхнего блока текста |
| `top_text_y` | INTEGER \| NULL | Y-координата верхнего блока текста |
| `top_text_width` | INTEGER \| NULL | Ширина верхнего текстового блока |
| `bottom_text_x` | INTEGER \| NULL | X-координата нижнего блока текста |
| `bottom_text_y` | INTEGER \| NULL | Y-координата нижнего блока текста |
| `bottom_text_width` | INTEGER \| NULL | Ширина нижнего текстового блока |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Дата создания |

### `generated_images`

| Поле | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | Идентификатор сгенерированного изображения |
| `template_id` | INTEGER FK -> templates.id | Шаблон, по которому сгенерировано изображение |
| `user_id` | INTEGER FK -> users.id | Владелец изображения |
| `text_top` | TEXT \| NULL | Верхний текст |
| `text_bottom` | TEXT \| NULL | Нижний текст |
| `image_path` | TEXT | Относительный путь к итоговому файлу |
| `share_token` | TEXT UNIQUE | Публичный токен для шаринга |
| `created_at` | DATETIME DEFAULT CURRENT_TIMESTAMP | Дата генерации |

Индексы:
- `ind_generated_images_user_id` на `generated_images(user_id)` для ускорения выборки личной галереи.

## 1.5. Ключевые технические решения

- Backend: `FastAPI` + `Pydantic` + `SQLite`.
  - Причина: быстрый старт, строгая валидация схем, простое локальное хранение данных для тестового проекта.
- Auth: session cookie (`itsdangerous` для подписи).
  - Причина: браузерный сценарий без необходимости вручную прокидывать Bearer токен.
- Обработка изображений: `Pillow`.
  - Причина: базовая генерация/preview мемов (текст, шрифт, цвет, layout) без внешних сервисов.
- Миграции: `Alembic`.
  - Причина: управляемая эволюция схемы БД и повторяемое разворачивание окружения.
- Frontend: ванильный JS + HTML/CSS (SPA с hash-routing).
  - Причина: минимальный стек, прозрачная логика, быстрое итеративное развитие UI.
- Rate limit: `slowapi`.
  - Причина: простая защита endpoint’ов preview/generate от спама.

Внешние API:
- Не используются.
