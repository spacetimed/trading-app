.PHONY: backend frontend test test-backend test-frontend lint-frontend build-frontend

backend:
	cd backend && venv/bin/uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && ./run_tests.sh

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

test-frontend: lint-frontend build-frontend

test: test-backend test-frontend
