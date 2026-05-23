# Automation Exercise — UI + API Tests

![Tests](https://github.com/svetlanastepanina1-debug/autotests_automationexercise/actions/workflows/tests.yml/badge.svg)

Автотесты для [Automation Exercise](https://automationexercise.com): страница продуктов и REST API из [списка API](https://automationexercise.com/api_list).

| Набор | Технологии | Паттерн | Запуск |
|-------|------------|---------|--------|
| **API** (24 теста) | pytest, requests | API Client + Service Object, AAA | `pytest -m api` — браузер не нужен |
| **UI** (70 тестов) | pytest, selenium | Page Object Model | `pytest -m ui --headless` — нужен Chrome |

Тесты ходят на **живой** сайт `automationexercise.com` — нужен интернет.

---

## Быстрый старт (первый запуск)

Выполните команды из корня репозитория `autotests_automationexercise`:

```bash
# 1. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1

# 2. Зависимости
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt   # Ruff + pre-commit (опционально)

# 3. API-тесты (рекомендуется начать с них — без Chrome)
pytest -m api -v

# 4. UI smoke (один тест)
pytest tests/test_products_page.py::TestPageLoad::test_page_title -v --headless

# 5. Все UI-тесты
pytest -m ui -v --headless
```

Опционально — для **всех** API-тестов, включая логин (API 7–8):

```bash
cp .env.example .env
# отредактируйте .env: TEST_USER_EMAIL и TEST_USER_PASSWORD — учётная запись,
# зарегистрированная на https://automationexercise.com (Signup/Login)
pytest -m api -v
```

Без `.env` пройдут 22 API-теста, 2 теста логина будут `skipped`.

---

## Стек

- Python 3.9+ (проверено на 3.14)
- pytest, pytest-html
- **API:** requests, python-dotenv, faker
- **UI:** selenium + Selenium Manager (chromedriver вручную не ставится)

---

## Что проверяют тесты

### API (14 сценариев с api_list)

- список товаров и брендов (GET)
- неподдерживаемые методы (POST/PUT/DELETE → `responseCode` 405)
- поиск товара и ошибка без параметра `search_product`
- verify login: валидный / невалидный / без email / DELETE
- жизненный цикл пользователя: create → update → get by email → delete

### UI

**`/products`** — загрузка, поиск, карточки, модалка корзины, сайдбар категорий/брендов, переход в детали товара; углубление: фильтр Women→Dress, бренд Polo, заголовок `Searched Products`, два товара в корзине.

**`/product_details`** — имя, цена, изображение, количество, отзыв, сайдбар, навигация назад в Products.

**`/view_cart`** — пустая корзина, строки после добавления, совпадение с карточкой каталога, `цена × qty = total`, удаление, checkout + сверка заказа на `/checkout` (с `.env`).

**`/login`** — формы Login/Signup, неверный пароль, успешный вход и logout (с `.env`).

---

## Структура проекта

```text
autotests_automationexercise/
├── api/
│   ├── client/api_client.py       # HTTP transport
│   ├── config/settings.py         # .env → BASE_URL, credentials
│   ├── models/user_factory.py
│   └── services/                    # Products, Brands, Search, Auth, User
├── tests/
│   ├── api/                       # @pytest.mark.api
│   ├── test_products_page.py      # @pytest.mark.ui
│   ├── test_product_details.py
│   ├── test_products_deepening.py
│   ├── test_cart.py
│   └── test_login.py
├── ui/pages/                      # POM: products, cart, login, checkout, …
├── ui/utils/pricing.py            # parse Rs. amounts for business asserts
├── conftest.py                    # UI: driver, --headless
├── tests/api/conftest.py          # API: api_client, services, registered_user
├── pytest.ini
├── .env.example
└── requirements.txt
```

---

## Архитектура

### API: Client → Service → Test (AAA)

```text
test  →  products_service.get_products()  →  ApiClient  →  automationexercise.com/api
         ↑ fixture (DI)
```

- **Arrange** — fixtures (`registered_user`, `valid_user_payload`)
- **Act** — один вызов метода Service
- **Assert** — `response.json["responseCode"]`, `message`, структура JSON

> Сайт часто отвечает **HTTP 200** при ошибке; смотрите `responseCode` в теле JSON.

### UI: Page Object Model

- `ui/pages/*.py` — локаторы и действия по страницам
- `tests/test_*.py` — сценарии (TC / PD / C / L / P)
- `conftest.py` — `driver`, `--headless`, `existing_user` из `.env`

---

## Переменные окружения

Скопируйте шаблон и при необходимости измените значения:

```bash
cp .env.example .env
```

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `API_BASE_URL` | Базовый URL API | `https://automationexercise.com/api` |
| `API_TIMEOUT` | Таймаут запросов (сек) | `30` |
| `TEST_USER_EMAIL` | Email для API 7–8 и UI login/checkout | — (тесты skip) |
| `TEST_USER_PASSWORD` | Пароль для API 7–8 и UI login/checkout | — (тесты skip) |

---

## Линтер (Ruff)

```bash
pip install -r requirements-dev.txt
ruff check .              # проверка
ruff check . --fix        # автоисправление
ruff format .             # форматирование
ruff format --check .     # только проверка формата (как в CI)
```

### Pre-commit (перед каждым коммитом)

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files   # первый прогон по всему проекту
```

В CI job **Lint (Ruff)** запускается перед `api-tests` и `ui-tests`.

---

## Запуск тестов

### API

```bash
pytest -m api -v
pytest tests/api/test_products_list.py -v
```

### UI

```bash
pytest -m ui -v --headless
pytest tests/test_products_page.py::TestPageLoad::test_page_title -v --headless
pytest tests/test_product_details.py -v --headless   # PD-01…PD-09
pytest tests/test_cart.py tests/test_login.py tests/test_products_deepening.py -v --headless
```

### Всё сразу

```bash
pytest tests/ -v --headless
```

### HTML-отчёт

```bash
pytest tests/ -v --headless --html=report.html --self-contained-html
```

---

## Системные требования

| Набор | Требования |
|-------|------------|
| API | Python 3.9+, интернет |
| UI | + Google Chrome, интернет (первый раз — Selenium Manager скачает driver) |

Проверка:

```bash
python3 --version
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version   # macOS
```

---

## Установка с нуля (подробно)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/svetlanastepanina1-debug/autotests_automationexercise.git
cd autotests_automationexercise
```

### 2–4. venv и зависимости

См. [Быстрый старт](#быстрый-старт-первый-запуск).

### 5. `.env` (опционально)

Нужен только если хотите запускать API 7–8 без `skipped`. Учётная запись должна быть создана на сайте через **Signup/Login**.

---

## Типовые проблемы

### API: 2 теста skipped

Не заданы `TEST_USER_EMAIL` / `TEST_USER_PASSWORD` в `.env`. Остальные API-тесты это не блокирует.

### UI: `SessionNotCreatedException` — ChromeDriver vs Chrome

Сообщение вида *«ChromeDriver only supports Chrome version 146», Current browser version is 148* значит, что в `PATH` лежит **устаревший** `chromedriver` (часто `/usr/local/bin/chromedriver`).

**Решение 1 (в проекте уже учтено):** `conftest.py` временно убирает такой driver из `PATH` и использует Selenium Manager.

**Решение 2 (на машине):** удалить или переименовать старый драйвер:

```bash
sudo mv /usr/local/bin/chromedriver /usr/local/bin/chromedriver.bak
```

Затем снова: `pytest -m ui -v --headless`

### UI: браузер не стартует

Установите Google Chrome. Первый запуск UI может быть долгим — Selenium Manager подбирает chromedriver.

### Нестабильные падения

Сайт недоступен, медленный ответ или изменился DOM/API. Повторите прогон; для UI используйте `--headless`.

### `NotOpenSSLWarning` (macOS)

Предупреждение urllib3 на системном Python. Для стабильности используйте Python из [python.org](https://www.python.org/) или pyenv.

---

## Что не коммитить

`.venv/`, `.pytest_cache/`, `.env`, `report.html`, `*.log`, `.DS_Store` — уже в `.gitignore`.

---

## CI (GitHub Actions)

В репозитории есть workflow [`.github/workflows/tests.yml`](.github/workflows/tests.yml):

| Job | Команда | Нужен Chrome |
|-----|---------|--------------|
| `lint` | `ruff check` + `ruff format --check` | нет |
| `api-tests` | `pytest -m api` | нет |
| `ui-tests` | `pytest -m ui --headless` | да (ставится автоматически) |

`api-tests` и `ui-tests` запускаются только после успешного `lint`.

### Badge в README

В начале README уже есть статус workflow:

```markdown
![Tests](https://github.com/svetlanastepanina1-debug/autotests_automationexercise/actions/workflows/tests.yml/badge.svg)
```

Формула: `https://github.com/<логин>/<репозиторий>/actions/workflows/<имя-workflow>.yml/badge.svg`

После push badge станет зелёным, если последний прогон CI успешен.

### Настройка один раз

1. Закоммитьте и запушьте код на GitHub (ветка `main` или `master`).
2. На GitHub: **Settings → Secrets and variables → Actions → New repository secret**:
   - `TEST_USER_EMAIL` — email с automationexercise.com
   - `TEST_USER_PASSWORD` — пароль
3. Без secrets API 7–8 в CI будут `skipped` (как локально без `.env`).
4. Проверка: вкладка **Actions** → workflow **Tests** → зелёные `api-tests` и `ui-tests`.

Запуск вручную: **Actions → Tests → Run workflow**.

### Артефакты CI (HTML-отчёты и скриншоты)

После каждого прогона (даже при падении тестов) в **Actions → выберите run → Artifacts**:

| Артефакт | Содержимое |
|----------|------------|
| `api-test-report` | `api-report.html` — отчёт pytest-html по API |
| `ui-test-artifacts` | `ui-report.html` + папка `screenshots/` |

Скачайте zip, откройте `ui-report.html` в браузере. При падении UI-теста в `screenshots/` будет PNG с экраном в момент ошибки.

Локально те же отчёты:

```bash
mkdir -p reports/screenshots
pytest -m api -v --html=reports/api-report.html --self-contained-html
pytest -m ui -v --headless --html=reports/ui-report.html --self-contained-html
```

Папка `reports/` в `.gitignore` — в репозиторий не коммитится.

---

## Дальнейшее развитие

- jsonschema для ответов API
- smoke E2E: сравнение `productsList` (API) и UI-страницы
- страницы product details / cart / login
