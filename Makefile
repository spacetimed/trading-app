.PHONY: backend frontend infra infra-down test test-backend test-frontend lint-frontend build-frontend

backend:
	set -a; [ ! -f backend/.env ] || . backend/.env; set +a; cd backend && venv/bin/uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

infra:
	docker compose up -d postgres redis

infra-down:
	docker compose down

test-backend:
	cd backend && ./run_tests.sh

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

test-frontend: lint-frontend build-frontend

test: test-backend test-frontend
