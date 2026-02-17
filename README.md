# Telegram Media Accelerator Bot

A Telegram bot with WebApp interface for fast media file uploading and sending, bypassing speed restrictions. The system uses Telegram as CDN through a private storage channel.

<img width="1185" height="920" alt="Untitled" src="https://github.com/user-attachments/assets/3a13785d-96b8-4506-a54e-727d883a06ac" />

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

## Project Structure

```
telegram-media-bot/
├── backend/               
│   ├── app/
│   │   ├── api/           
│   │   ├── bot/          
│   │   ├── core/          
│   │   ├── db/           
│   │   ├── services/     
│   │   └── utils/         
│   ├── alembic/           
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              
│   ├── src/
│   │   ├── components/   
│   │   ├── services/     
│   │   ├── hooks/        
│   │   └── types/        
│   ├── Dockerfile
│   └── package.json
├── nginx/                 
├── docker-compose.yml
└── .env.example
