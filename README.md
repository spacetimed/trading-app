# trading-app

### Overview
A full-stack paper-trading application that allows users to deposit virtual cash, place simulated market orders using real market data, and track portfolio holdings, account value, and profit/loss over time.

### Scope for MVP
Users can:
- Register/login
- Deposit/withdraw virtual cash
- Stock lookup and view price
- Place simulated market buy/sell orders
- View summary: trade history, cash balance, positions, PnL

Frontend
- Login/register pages — authentication flow 
- Dashboard page — supports all summary features above, poll live prices
- Forms — deposit, withdraw, buy, and sell

Backend:
- REST endpoints
- Validates inputs and requests
- Applies trading and account rules (sufficient cash, etc.)
- Fetch and cache real market data (Redis)
- Update database on actions (buy/sell/deposit)

Tests
- deposit increases cash
- withdraw decreases cash
- can’t over-withdraw
- buy works with enough cash    
- buy fails without enough cash
- sell works if shares owned
- sell fails if not enough shares

Data
- Real stock-market quote API
- Polling-based updates for MVP; websockets maybe

Database
- Schemas: Users, Transactions, Trades, Positions
- Users
	- id, email, password, created_at
- Transactions (cash in/out)
	- id, user_id, type (deposit|withdraw), amount
- Trades
	- id, user_id, symbol, side (buy|sell), quantity, price
- Positions
	- id, user_id, symbol, quantity, avg_cost

### Architecture
- Frontend: React, TypeScript, Vite
- Backend: FastAPI
- Database: PostgreSQL
- Cache: Redis
- Auth: JWT-based authentication
- Deployment: Docker, AWS 
### API
- POST /auth/register
- POST /auth/login
- GET /auth/me
- POST /account/deposit
- POST /account/withdraw
- GET /account/summary
- GET /market/quote/{symbol}
- POST /orders/buy
- POST /orders/sell
- GET /portfolio
- GET /trades

### Build order (tentative) 
- [ ] Create repository, clone locally
- [ ] Create rough project structure (frontend/ and backend/)
- [ ] Setup backend (FastAPI running)
- [ ] Setup PostgreSQL and connect DB
- [ ] Add /health endpoint
- [ ] Setup database schema (User, Transaction, Trade, Position)
- [ ] Implement auth endpoints (register, login, /me)
- [ ] Implement deposit and withdraw endpoints
- [ ] Integrate market data API + quote endpoint
- [ ] Implement buy and sell endpoints
- [ ] Implement portfolio and trades endpoints 
- [ ] Create tests alongside endpoints

(incomplete)
