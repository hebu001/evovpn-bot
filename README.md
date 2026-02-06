# EvoVPN Bot

Telegram-бот для продажи VPN-ключей (VLESS/Outline/WireGuard) с интеграцией Marzban, платёжными системами и партнёрской программой.

## Требования

- Сервер с Ubuntu 20.04+ (или Debian 11+)
- Docker и Docker Compose (v2)
- Telegram Bot Token (от [@BotFather](https://t.me/BotFather))
- Минимум 1 ГБ RAM, 10 ГБ диска

## Быстрая установка (новый сервер)

### 1. Установить Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### 2. Клонировать репозиторий

```bash
git clone https://github.com/hebu001/evovpn-bot.git
cd evovpn-bot
```

### 3. Создать файл конфигурации

```bash
cp .env.example .env
nano .env
```

Обязательно заполнить:

| Переменная | Описание |
|---|---|
| `TOKEN_MAIN` | Токен бота от @BotFather |
| `ADMINS_IDS` | ID администраторов `[123456789]` |
| `MY_ID_TELEG` | Ваш Telegram ID |
| `NAME_VPN_CONFIG` | Название VPN (только буквы и цифры) |
| `POSTGRES_PASSWORD` | Надёжный пароль для БД |

### 4. Запустить бота

```bash
docker compose up -d --build
```

### 5. Проверить работу

```bash
docker compose logs -f bot
```

Бот должен написать `✅Бот успешно запущен!`

## Миграция с SQLite (перенос данных со старого сервера)

Если у вас есть файл `db.db` от предыдущей установки бота:

### 1. Скопировать db.db на новый сервер

```bash
scp user@old-server:/path/to/db.db ./data/db.db
```

### 2. Запустить миграцию

```bash
chmod +x migrate_main.sh
./migrate_main.sh
```

Или указать путь к файлу напрямую:

```bash
./migrate_main.sh --sqlite-main /path/to/db.db
```

### Параметры миграции

| Флаг | Описание |
|---|---|
| `--sqlite-main PATH` | Путь к основной SQLite БД |
| `--truncate` | Очистить таблицы перед вставкой |
| `--fresh` | Удалить том Postgres и создать заново (ОПАСНО) |
| `--skip-backup` | Пропустить бекап SQLite файлов |
| `--skip-build` | Пропустить сборку Docker-образа |

## Структура проекта

```
.
├── bot.py                       # Основной код бота
├── docker-compose.yml           # Docker Compose конфигурация
├── Dockerfile                   # Сборка образа
├── requirements.txt             # Python зависимости
├── .env.example                 # Шаблон конфигурации
├── migrate_sqlite_to_postgres.py # Скрипт миграции SQLite → Postgres
├── migrate_main.sh              # Обёртка для запуска миграции
├── commandsgit.md               # Git-команды (шпаргалка)
├── data/
│   ├── lang.yml                 # Тексты и локализация
│   └── markup_inline.py         # Inline-клавиатуры
└── logs/                        # Логи (создаётся автоматически)
```

## Обновление бота

```bash
cd evovpn-bot
git pull
docker compose up -d --build
```

## Полезные команды

```bash
# Логи бота
docker compose logs -f bot

# Логи Postgres
docker compose logs -f postgres

# Перезапуск бота
docker compose restart bot

# Остановить всё
docker compose down

# Зайти в контейнер бота
docker exec -it vpn-bot bash

# Подключиться к PostgreSQL
docker exec -it vpn-bot-postgres psql -U vpn_bot -d vpn_bot
```

## Бекап базы данных

```bash
# Создать дамп PostgreSQL
docker exec vpn-bot-postgres pg_dump -U vpn_bot vpn_bot > backup.sql

# Восстановить из дампа
docker exec -i vpn-bot-postgres psql -U vpn_bot vpn_bot < backup.sql
```
