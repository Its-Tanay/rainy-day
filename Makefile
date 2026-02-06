.PHONY: help setup dev dev-clean test clean install db-seed logs stop restart

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh
	
dev:
	@echo "Starting development environment..."
	@docker-compose up

dev-clean:
	@echo "Starting development environment (clean build)..."
	@docker-compose up --build --force-recreate

stop:
	@echo "Stopping containers..."
	@docker-compose down

restart:
	@echo "Restarting containers..."
	@docker-compose restart

logs:
	@docker-compose logs -f

db-seed:
	@echo "Seeding database with sample data..."
	@docker-compose exec backend python seed.py
	@echo "\nDatabase seeded."

test:
	@echo "Running tests..."
	@docker-compose exec backend pytest

clean:
	@echo "Cleaning up Docker resources..."
	@docker-compose down -v --rmi all
	@echo "Cleanup complete."

install:
	@echo "Installing backend dependencies..."
	@cd server && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	@cd client && npm install
	@echo "Dependencies installed."
