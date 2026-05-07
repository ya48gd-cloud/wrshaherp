# ═══════════════════════════════════════════════════════════
#  Makefile — Heavy Equipment Workshop ERP
#  Usage: make <command>
# ═══════════════════════════════════════════════════════════

.PHONY: up down build seed logs shell-backend shell-db test clean restart

# ── Start all services ──────────────────────────────────────
up:
	docker compose up -d
	@echo ""
	@echo "✅  ERP is starting..."
	@echo "    Frontend  →  http://localhost"
	@echo "    API docs  →  http://localhost/docs"
	@echo "    API v1    →  http://localhost/api/v1"
	@echo ""

# ── Stop all services ───────────────────────────────────────
down:
	docker compose down

# ── Rebuild images (after code changes) ────────────────────
build:
	docker compose build --no-cache backend

# ── Seed demo data ──────────────────────────────────────────
seed:
	docker compose exec backend python seed.py

# ── View logs ───────────────────────────────────────────────
logs:
	docker compose logs -f backend

logs-all:
	docker compose logs -f

# ── Open shell inside backend container ────────────────────
shell-backend:
	docker compose exec backend bash

# ── Open psql shell ────────────────────────────────────────
shell-db:
	docker compose exec db psql -U erp_user -d heavy_erp

# ── Run migrations manually ────────────────────────────────
migrate:
	docker compose exec backend alembic upgrade head

# ── Rollback last migration ────────────────────────────────
rollback:
	docker compose exec backend alembic downgrade -1

# ── Quick API test ──────────────────────────────────────────
test:
	@echo "Testing API endpoints..."
	curl -s http://localhost/health | python3 -m json.tool
	curl -s http://localhost/api/v1/inventory/materials | python3 -m json.tool | head -30
	curl -s http://localhost/api/v1/accounting/dashboard | python3 -m json.tool

# ── Full reset (delete volumes) ─────────────────────────────
clean:
	docker compose down -v
	@echo "⚠️  All data volumes deleted"

# ── Restart backend only ────────────────────────────────────
restart:
	docker compose restart backend
