# KHLbot

Telegram-бот с расписанием и результатами матчей КХЛ, подпиской на уведомления и выбором любимой команды.

## Возможности
- `/start` — меню и краткая справка
- `/matches` или `/today` — матчи на сегодня
- `/tomorrow` — матчи на завтра
- `/week` — ближайшие матчи на 7 дней
- `/subscribe` / `/unsubscribe` — уведомления о матчах
- `/team` — выбор любимой команды
- `/help` — список команд

Данные расписания берутся из публичного KHL Webcaster mobile API. Внешний API не является частью этого проекта и может менять формат или ограничивать доступ.

## Локальный запуск
Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# заполнить BOT_TOKEN
python -m app
```

Локальная команда `python -m app` запускает long polling. На Render используется HTTP webhook через FastAPI; публичный URL Render приложение получает автоматически из `RENDER_EXTERNAL_URL`.

## Render Free (без платного Background Worker)
Самый быстрый путь — подключить репозиторий через **New → Blueprint**: Render прочитает `render.yaml` и создаст Free Web Service. Либо создай **Web Service** вручную:
- Runtime: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.web:app --host 0.0.0.0 --port $PORT`
- Instance Type: `Free`

Environment Variables:
- `BOT_TOKEN` — токен от @BotFather
- `WEBHOOK_URL` — необязательный публичный URL; если не задан, Render URL берётся автоматически из `RENDER_EXTERNAL_URL`
- `WEBHOOK_SECRET` — случайная строка из букв и цифр, 32+ символа
- `JOB_TOKEN` — отдельная случайная строка для endpoint уведомлений
- `DATABASE_URL` — необязательно для первого запуска; по умолчанию SQLite. Для сохранения пользователей между перезапусками подключи бесплатный PostgreSQL (например, Neon) и укажи URL вида `postgresql://...`; приложение автоматически преобразует его в формат psycopg.
- `TIMEZONE` — часовой пояс расписания, по умолчанию `Europe/Moscow`
- `KHL_SEASON` — сезон по году окончания, по умолчанию определяется автоматически

После деплоя проверь `https://<service>.onrender.com/health`.

### Уведомления на бесплатном Render
Free Web Service засыпает после периода без запросов. Поэтому сам процесс не может гарантировать точные фоновые уведомления, пока сервис спит. В репозитории есть GitHub Actions workflow `.github/workflows/notify.yml`: он вызывает защищённый endpoint примерно раз в 10 минут и будит сервис.

В GitHub → Settings → Secrets and variables → Actions добавь:
- `RENDER_APP_URL` — URL Render-сервиса
- `JOB_TOKEN` — то же значение, что в Render

GitHub Actions на бесплатном тарифе имеет ограничения и расписание может задерживаться. Уведомления отправляются о матчах, начинающихся в ближайшие 30 минут; при холодном старте возможна задержка. Важно: запуск workflow каждые 10 минут не даёт Render уснуть и может расходовать почти весь лимит 750 бесплатных часов в месяц (до примерно 744 часов за 31 день). Если уведомления не нужны, отключи workflow — бот будет просыпаться по входящему сообщению, но первый ответ после простоя может задержаться примерно на минуту.

### Важно про хранение данных
Файловая система Render Free эфемерная: SQLite-файл может исчезнуть при redeploy/restart. Для сохранения подписок подключи внешнюю бесплатную PostgreSQL БД и задай `DATABASE_URL`. Не добавляй токен Telegram в Git.

## Проверки
```bash
pip install -r requirements-dev.txt
pytest -q
```
