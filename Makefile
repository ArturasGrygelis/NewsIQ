# NewsIQ Docker Commands
# Run these commands with: make <command>
# Or on Windows PowerShell, just copy the command after the colon

.PHONY: help build up down restart logs clean backup restore

help: ## Show this help message
	@echo "NewsIQ Docker Commands:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs"
	@echo "  make clean     - Stop and remove all containers, networks, and volumes"
	@echo "  make backup    - Backup ChromaDB data"
	@echo "  make restore   - Restore ChromaDB data"

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs only
	docker-compose logs -f backend

logs-frontend: ## View frontend logs only
	docker-compose logs -f frontend

clean: ## Stop and remove everything
	docker-compose down -v

rebuild: ## Rebuild and restart
	docker-compose up -d --build

ps: ## Show running containers
	docker-compose ps

backup: ## Backup ChromaDB data
	docker run --rm -v newsiq_chroma-data:/data -v $${PWD}:/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .
	@echo "Backup created: chroma-backup.tar.gz"

restore: ## Restore ChromaDB data from backup
	docker-compose down
	docker run --rm -v newsiq_chroma-data:/data -v $${PWD}:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/chroma-backup.tar.gz -C /data"
	docker-compose up -d
	@echo "Backup restored and services restarted"
