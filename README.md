# Drone-ej

Drone-ej is a Telegram-first market intelligence bot designed to monitor forex and crypto news, rank high-impact macro events, and push relevant alerts to users in near real time.

The project is intentionally structured as a starter repo so you can run it locally, extend it with real data sources, and deploy it in Docker or a VPS.

## Features
- Telegram bot interface
- Forex + crypto watchlist support
- High-impact event recognition for CPI, NFP, FOMC, ECB, BoE, BoJ, and more
- Demo news feed + alert ranking engine
- Docker and Redis/Postgres setup for local development
- Modular services for future source integrations

## Quick start

### 1. Create a Telegram bot
1. Open Telegram and message `@BotFather`
2. Run `/newbot`
3. Copy the token and set it in `.env`

### 2. Configure environment
Copy the example file:

```bash
cp .env.example .env
```

Then update:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
APP_ENV=development
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the bot

```bash
python -m app.main
```

### 5. Optional Docker run

```bash
docker-compose up --build
```

## Included commands
- `/start` — welcome message
- `/help` — show commands
- `/watchlist` — show current asset watchlist
- `/demo` — show sample market alerts
- `/clear` — clear user conversation context

## Project structure

```text
app/
  __init__.py
  config.py
  main.py
  models.py
  services/
    impact_service.py
    news_service.py
    telegram_bot.py
README.md
requirements.txt
Dockerfile
docker-compose.yml
.env.example
```

## Current scope
This repo is a working starter template. It includes demo market alerts and high-impact event logic, but production integrations for live news feeds and economic calendars should be added through the service layer.

## Recommended next upgrades
- Connect RSS feeds and Google/Bing News APIs
- Add live economic calendar polling
- Add PostgreSQL persistence for user watchlists
- Add Redis caching and background jobs
- Add Telegram button menus and rich formatting
- Add webhook or polling scheduler for real-time delivery

## Example high-impact forex events monitored
- NFP
- CPI
- Core CPI
- PPI
- GDP
- FOMC
- ECB rate decisions
- BoE rate decisions
- BoJ policy decisions
- PMIs and labor data
