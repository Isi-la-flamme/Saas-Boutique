# POS Backend

Offline-first POS System with auto-sync

## Description

Point of Sale backend with:
- Offline-first architecture
- Automatic sync when connection returns
- Multi-tenant support
- Last write wins conflict resolution

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (online) / SQLite (offline)
- JWT Authentication

### Backend start

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 

#### Frontend start
npm run dev