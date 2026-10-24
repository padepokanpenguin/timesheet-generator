.PHONY: install dev-api dev-web test lint format gen-api build check up

install:            ## Pasang semua dependensi (Python + JS)
	uv sync --all-packages
	pnpm install

dev-api:            ## API di http://localhost:8000 (docs: /docs)
	cd apps/api && uv run --all-packages uvicorn app.main:app --reload

dev-web:            ## Web di http://localhost:5173 (proxy /api -> :8000)
	pnpm --filter @timesheet/web dev

test:               ## Tes semua paket Python
	uv run --all-packages pytest

lint:
	uv run --all-packages ruff check .
	uv run --all-packages ruff format --check .

format:
	uv run --all-packages ruff check --fix .
	uv run --all-packages ruff format .

gen-api:            ## Ekspor OpenAPI -> tipe TypeScript di packages/api-client
	pnpm gen:api

check:              ## Type-check TS/Svelte
	pnpm check

build:
	pnpm build

up:                 ## Jalankan lewat Docker
	docker compose up --build
