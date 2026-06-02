# Architecture

## Frontend

- Next.js 15 App Router
- TypeScript + TailwindCSS
- Landing page enterprise premium
- Auth screen and authenticated AI portal
- Floating AI consultant experience as the primary CTA

## Backend

- Flask API with SQLAlchemy models
- JWT access and refresh tokens
- Socket.IO for realtime consultant sessions
- Celery for background jobs
- OpenAPI document endpoint at `/api/openapi.json`

## Data and AI

- PostgreSQL for core CRM and platform data
- Redis for Celery broker/result backend
- Qdrant for RAG and semantic retrieval
- OpenAI and other model providers as integration targets

## Core Workflows

- Visitor speaks with AI consultant
- AI qualifies and scores the lead
- AI recommends services and schedules a meeting
- AI generates meeting prep, summaries, and proposal drafts
- Human consultant intervenes only on high-value or ambiguous opportunities

## Deployment

- Frontend: Vercel
- Backend: Railway
- PostgreSQL: Railway
- Redis: Railway
- Qdrant: Docker
