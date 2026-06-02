# AI Enterprise Consulting Platform

Monorepo de départ pour une plateforme de conseil IA enterprise avec consultant conversationnel au centre de l'expérience.

Workspaces:
- packages/frontend  (Next.js 15 + TypeScript + Tailwind)
- services/backend   (Flask + SQLAlchemy + JWT + Celery + Socket.IO)
- infra              (Docker Compose, PostgreSQL, Redis, Qdrant)
- docs               (architecture et notes techniques)

Ce scaffold inclut:
- Landing page premium orientée consultant IA
- Portail authentifié avec espace de consultation
- Backend API pour auth, leads, scheduling, knowledge base et analytics
- Contrats OpenAPI et base de realtime consulting via WebSockets
