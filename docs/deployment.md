# BreakTraceFix AI - Deployment Guide

## Deployment Options

### 1. Vercel Serverless Deployment
- Configured via `vercel.json` and `api/index.py`.
- Rewrites `/api/(.*)` to Python ASGI serverless handler.
- Frontend builds statically via Vite into `dist/`.

### 2. Standalone Local Execution
```bash
# Backend
cd breaktracefix-ai
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

### 3. Docker Compose Deployment
```bash
docker-compose up --build
```
Includes:
- `breaktracefix-backend` (Port 8000)
- `postgres` (Port 5432)
- `redis` (Port 6379)

