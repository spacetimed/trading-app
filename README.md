# Trading Application

A full-stack paper-trading app for practicing stock trading with virtual cash. Users will be able to create an account, manage a cash balance, place simulated market orders using real quote data, and track their portfolio, trade history, account value, and profit/loss over time.

This is intended as an MVP first, with the core backend and frontend flows built before adding deployment and production-style infrastructure.

## MVP Scope

Users should be able to:

- register and log in
- deposit and withdraw virtual cash
- look up a stock symbol and view a current price
- place simulated market buy and sell orders
- view cash balance, positions, trade history, and PnL

## Stack

- Frontend: React, Vite, MUI
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- Cache: Redis for quote caching, planned
- Auth: JWT-based authentication
- Deployment: Docker and a free hosting target, planned

## Local Development

Common commands are exposed from the root `Makefile`.

Start the backend:

```bash
make backend
```

Start the frontend:

```bash
make frontend
```

Run backend tests and frontend checks:

```bash
make test
```

Other available checks:

```bash
make test-backend
make lint-frontend
make build-frontend
make test-frontend
```

## Market Data

For the MVP, quote data uses free providers without API keys. The app tries Yahoo Finance chart data first, falls back to Stooq CSV data, and then falls back to a small local fake quote list for supported symbols during outages or local testing. Redis quote caching is planned so repeated quote requests can avoid unnecessary external calls.

## Frontend

Current screens and flows:

- login/register pages for authentication
- dashboard for account summary, positions, trade history, and PnL
- forms for deposit, withdraw, buy, and sell actions
- quote lookup
- loading, empty, and error states for the main dashboard flows

## Backend

The backend will expose REST endpoints and handle the main application rules:

- validate request bodies and user input
- create and authenticate users
- apply account rules, such as sufficient cash for buys
- apply position rules, such as sufficient shares for sells
- fetch real market quote data
- cache quote data where useful
- write account, trade, and position changes to the database

## Manual Smoke Test

After starting the backend and frontend, a basic frontend flow is:

- register or log in
- deposit virtual cash
- look up a stock symbol
- buy shares
- verify cash, positions, and trade history update
- sell shares
- withdraw cash
- verify account summary updates

## Data Model

Initial database tables:

### Users

- id
- email
- password
- created_at

### Transactions

Cash deposits and withdrawals.

- id
- user_id
- type: deposit or withdraw
- amount

### Trades

Executed simulated orders.

- id
- user_id
- symbol
- side: buy or sell
- quantity
- price

### Positions

Current holdings per user and symbol.

- id
- user_id
- symbol
- quantity
- avg_cost

## API Plan

Auth:

- POST `/auth/register`
- POST `/auth/login`
- GET `/auth/me`

Account:

- POST `/account/deposit`
- POST `/account/withdraw`
- GET `/account/summary`

Market:

- GET `/market/quote/{symbol}`

Orders and portfolio:

- POST `/orders/buy`
- POST `/orders/sell`
- GET `/portfolio`
- GET `/trades`

## Test Plan

Core backend behavior to test:

- deposit increases cash
- withdraw decreases cash
- users cannot over-withdraw
- buy works when the user has enough cash
- buy fails when the user does not have enough cash
- sell works when the user owns enough shares
- sell fails when the user does not own enough shares

Auth tests:

- register creates a user
- duplicate email is rejected
- short password is rejected
- login succeeds with valid credentials
- login fails with a missing email
- login fails with the wrong password

## Build Order

- [x] Create repository and local project structure
- [x] Set up backend directory
- [x] Set up FastAPI with `/health`
- [x] Connect PostgreSQL through SQLAlchemy
- [x] Add initial database models
- [x] Implement `/auth/register`
- [x] Add basic register tests
- [x] Implement `/auth/login`
- [x] Add basic login tests
- [x] Add JWT access tokens
- [x] Add `/auth/me`
- [x] Implement deposit and withdraw endpoints
- [x] Integrate market data API and quote endpoint
- [x] Implement buy and sell endpoints
- [x] Implement portfolio and trades endpoints
- [x] Build frontend login/register flow
- [x] Build dashboard and trading forms
- [ ] Add Redis quote caching
- [ ] Dockerize local development
- [ ] Deploy MVP

## Notes

The current focus is moving from MVP behavior into production-style polish. Some implementation details are intentionally simple for now and should be revisited later, especially password hashing, database migrations, environment-based configuration, Redis caching, Docker, and deployment.
