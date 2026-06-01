# Trading Application

A full-stack paper-trading app for simulated stock trading with virtual cash.

Users can register, log in, deposit and withdraw cash, look up stock quotes, place buy/sell orders, and track positions, trade history, and unrealized PnL.

## Demo

- Frontend: <https://trading-app-demo-spacetimed.vercel.app>
- Backend health: <https://trading-app-backend-ulze.onrender.com/health>

The backend runs on Render's free tier, so the first request after inactivity can be slow.

## Stack

- Frontend: React, Vite, MUI
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- Cache: Redis
- Auth: JWT
- Deployment: Vercel, Render, Supabase, Upstash

## Features

- Email/password registration and login
- JWT-protected account, portfolio, order, and trade endpoints
- Virtual cash deposits and withdrawals
- Quote lookup using Yahoo Finance, Stooq, and local fallback data
- Redis quote caching with a short TTL
- Simulated market buy and sell orders
- Position tracking with average cost
- Portfolio market value and unrealized PnL
- Trade history
- React dashboard for the main trading flow

## Local Development

Copy the backend environment example:

```bash
cp backend/.env.example backend/.env
```

Required backend variables:

```txt
DATABASE_URL=postgresql://username:password@localhost:5432/trading_app
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=replace-me-with-a-long-random-secret
FRONTEND_ORIGIN=http://localhost:5173
```

The backend does not provide code-level defaults for required configuration. Missing variables fail startup.

Start local Postgres and Redis with Docker Compose:

```bash
make infra
```

The Compose Postgres service uses port `5433` to avoid conflicting with a local Postgres on `5432`.

```txt
DATABASE_URL=postgresql://trading_app:trading_app@localhost:5433/trading_app
REDIS_URL=redis://localhost:6379/0
```

Run the app:

```bash
make backend
make frontend
```

Run checks:

```bash
make test
```

Other commands:

```bash
make test-backend
make lint-frontend
make build-frontend
make test-frontend
make infra-down
```

## Deployment

Production services:

- Vercel hosts the React/Vite frontend
- Render runs the FastAPI backend from `backend/Dockerfile`
- Supabase hosts Postgres
- Upstash hosts Redis

Frontend environment:

```txt
VITE_API_URL=https://trading-app-backend-ulze.onrender.com
```

Backend environment:

```txt
DATABASE_URL=postgresql://...
REDIS_URL=rediss://...
SECRET_KEY=...
FRONTEND_ORIGIN=https://trading-app-demo-spacetimed.vercel.app
```

## API

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Account:

- `POST /account/deposit`
- `POST /account/withdraw`
- `GET /account/summary`

Market:

- `GET /market/quote/{symbol}`

Trading:

- `POST /orders/buy`
- `POST /orders/sell`
- `GET /portfolio`
- `GET /trades`

## Data Model

- `users`: account credentials and cash balance
- `transactions`: cash deposits and withdrawals
- `trades`: executed buy/sell orders
- `positions`: current holdings by user and symbol

## Status

The MVP is deployed and supports the main paper-trading flow end to end.

Next improvements:

- bcrypt/passlib password hashing
- Alembic migrations
- login/register rate limiting
- GitHub Actions CI
- deployment hardening
