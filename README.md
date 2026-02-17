# Telegram Media Accelerator Bot

A Telegram bot with WebApp interface for fast media file uploading and sending, bypassing speed restrictions. The system uses Telegram as CDN through a private storage channel.

<img width="592" height="460" alt="Untitled" src="https://github.com/user-attachments/assets/3a13785d-96b8-4506-a54e-727d883a06ac" />

## Features

- Video upload through WebApp (React)
- FFmpeg video processing (thumbnail generation, streaming optimization)
- Telegram as free CDN storage
- Instant video sharing via inline mode
- Tiered system (Free/Pro)
- PostgreSQL database (Redis optional for production)
- Docker deployment

## Architecture

- **Backend**: Python 3.10+ (FastAPI + aiogram 3.4+)
- **Frontend**: React 18+ with TypeScript, Vite, Tailwind CSS, Framer Motion
- **Database**: PostgreSQL 15+ (required)
- **Cache**: Redis 7 (optional - for production caching/rate limiting)
- **Proxy**: Nginx
- **Processing**: FFmpeg

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run with Docker Compose:

```bash
docker-compose up -d
```

**Note**: Redis is optional. The app works without it. To enable Redis for production, uncomment the `redis` service in [docker-compose.yml](docker-compose.yml) and set `REDIS_HOST=redis` in `.env`.

## Project Structure

```
telegram-media-bot/
├── backend/                # Python FastAPI + aiogram backend
│   ├── app/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── bot/           # Telegram bot handlers
│   │   ├── core/          # Core configuration
│   │   ├── db/            # Database models and CRUD
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   ├── hooks/        # Custom hooks
│   │   └── types/        # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── nginx/                 # Nginx configuration
├── docker-compose.yml
└── .env.example

```

## Configuration

See `.env.example` for all configuration options.

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## License

MIT
