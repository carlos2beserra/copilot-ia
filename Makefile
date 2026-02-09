# =============================================================================
# Copilot-IA - Makefile
# =============================================================================
# Comandos utilitários para desenvolvimento, testes e deploy
#
# Uso: make <comando>
# Ajuda: make help
# =============================================================================

.PHONY: help install install-dev setup clean clean-all \
        lint format type-check check \
        test test-cov test-verbose \
        run run-dev api \
        docker-build docker-up docker-down docker-logs docker-shell \
        up down logs restart \
        docs notebook \
        env-check version

# -----------------------------------------------------------------------------
# Variáveis
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := pip
PROJECT_NAME := copilot-ia
SRC_DIR := src
TEST_DIR := tests
DOCKER_COMPOSE := docker-compose

# Cores para output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

# =============================================================================
# AJUDA
# =============================================================================

help: ## 📖 Mostra esta mensagem de ajuda
	@echo ""
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           🤖 Copilot-IA - Comandos Disponíveis                ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# INSTALAÇÃO E SETUP
# =============================================================================

install: ## 📦 Instala dependências de produção
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt

install-dev: ## 📦 Instala dependências de desenvolvimento
	@echo "$(BLUE)📦 Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

setup: ## 🚀 Setup completo do projeto (venv + deps + env)
	@echo "$(BLUE)🚀 Configurando projeto...$(NC)"
	@if [ ! -d ".venv" ]; then \
		echo "$(YELLOW)Criando ambiente virtual...$(NC)"; \
		$(PYTHON) -m venv .venv; \
	fi
	@echo "$(YELLOW)Ativando venv e instalando deps...$(NC)"
	@. .venv/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt && $(PIP) install -e ".[dev]"
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)Criando arquivo .env a partir do exemplo...$(NC)"; \
		cp env.example .env; \
		echo "$(RED)⚠️  Edite o arquivo .env com suas chaves de API!$(NC)"; \
	fi
	@mkdir -p data/cache data/outputs logs
	@echo "$(GREEN)✅ Setup concluído!$(NC)"

# =============================================================================
# QUALIDADE DE CÓDIGO
# =============================================================================

lint: ## 🔍 Executa linter (ruff)
	@echo "$(BLUE)🔍 Executando linter...$(NC)"
	ruff check $(SRC_DIR) $(TEST_DIR)

lint-fix: ## 🔧 Corrige problemas de lint automaticamente
	@echo "$(BLUE)🔧 Corrigindo problemas de lint...$(NC)"
	ruff check $(SRC_DIR) $(TEST_DIR) --fix

format: ## 🎨 Formata código (black)
	@echo "$(BLUE)🎨 Formatando código...$(NC)"
	black $(SRC_DIR) $(TEST_DIR) examples/

format-check: ## 🎨 Verifica formatação sem modificar
	@echo "$(BLUE)🎨 Verificando formatação...$(NC)"
	black $(SRC_DIR) $(TEST_DIR) examples/ --check

type-check: ## 🔬 Verifica tipos (mypy)
	@echo "$(BLUE)🔬 Verificando tipos...$(NC)"
	mypy $(SRC_DIR)

check: lint format-check type-check ## ✅ Executa todas as verificações

# =============================================================================
# TESTES
# =============================================================================

test: ## 🧪 Executa testes
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	pytest $(TEST_DIR)/

test-cov: ## 📊 Executa testes com cobertura
	@echo "$(BLUE)📊 Executando testes com cobertura...$(NC)"
	pytest $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)📁 Relatório HTML gerado em: htmlcov/index.html$(NC)"

test-verbose: ## 🧪 Executa testes com output detalhado
	@echo "$(BLUE)🧪 Executando testes (verbose)...$(NC)"
	pytest $(TEST_DIR)/ -v --tb=long

test-watch: ## 👀 Executa testes em modo watch
	@echo "$(BLUE)👀 Modo watch ativado...$(NC)"
	pytest-watch -- $(TEST_DIR)/

# =============================================================================
# EXECUÇÃO
# =============================================================================

run: ## ▶️  Executa a API
	@echo "$(BLUE)▶️  Iniciando API...$(NC)"
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

run-dev: ## 🔄 Executa a API em modo desenvolvimento (hot-reload)
	@echo "$(BLUE)🔄 Iniciando API em modo dev...$(NC)"
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

api: run-dev ## 🔄 Alias para run-dev

# =============================================================================
# DOCKER
# =============================================================================

docker-build: ## 🐳 Build da imagem Docker
	@echo "$(BLUE)🐳 Construindo imagem Docker...$(NC)"
	docker build -t $(PROJECT_NAME) .

docker-up: ## 🐳 Inicia containers (docker-compose)
	@echo "$(BLUE)🐳 Iniciando containers...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Containers iniciados!$(NC)"
	@echo "$(YELLOW)API: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Redis: localhost:6379$(NC)"

docker-up-full: ## 🐳 Inicia todos containers incluindo ChromaDB
	@echo "$(BLUE)🐳 Iniciando todos os containers...$(NC)"
	$(DOCKER_COMPOSE) --profile full up -d

docker-down: ## 🐳 Para containers
	@echo "$(BLUE)🐳 Parando containers...$(NC)"
	$(DOCKER_COMPOSE) down

docker-down-volumes: ## 🐳 Para containers e remove volumes
	@echo "$(BLUE)🐳 Parando containers e removendo volumes...$(NC)"
	$(DOCKER_COMPOSE) down -v

docker-logs: ## 📋 Mostra logs dos containers
	$(DOCKER_COMPOSE) logs -f

docker-logs-api: ## 📋 Mostra logs apenas da API
	$(DOCKER_COMPOSE) logs -f api

docker-shell: ## 🐚 Abre shell no container da API
	docker exec -it copilot-ia-api /bin/bash

docker-restart: down up ## 🔄 Reinicia containers

# Aliases curtos para Docker
up: docker-up ## 🐳 Alias para docker-up
down: docker-down ## 🐳 Alias para docker-down
logs: docker-logs ## 📋 Alias para docker-logs
restart: docker-restart ## 🔄 Alias para docker-restart

# =============================================================================
# UTILITÁRIOS
# =============================================================================

notebook: ## 📓 Inicia Jupyter Notebook
	@echo "$(BLUE)📓 Iniciando Jupyter Notebook...$(NC)"
	@. .venv/bin/activate && jupyter notebook notebooks/

env-check: ## 🔐 Verifica variáveis de ambiente
	@echo "$(BLUE)🔐 Verificando variáveis de ambiente...$(NC)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ Arquivo .env encontrado$(NC)"; \
		echo "$(YELLOW)Variáveis configuradas:$(NC)"; \
		grep -E "^[A-Z_]+=" .env | cut -d= -f1 | while read var; do \
			echo "  - $$var"; \
		done; \
	else \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute: make setup$(NC)"; \
	fi

version: ## 📌 Mostra versão do projeto
	@echo "$(BLUE)📌 Copilot-IA$(NC)"
	@grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2

tree: ## 🌳 Mostra estrutura do projeto
	@echo "$(BLUE)🌳 Estrutura do projeto:$(NC)"
	@tree -I '__pycache__|*.egg-info|.git|.venv|node_modules|htmlcov|.mypy_cache|.pytest_cache' -L 3

# =============================================================================
# LIMPEZA
# =============================================================================

clean: ## 🧹 Remove arquivos temporários
	@echo "$(BLUE)🧹 Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

clean-all: clean ## 🧹 Remove tudo (incluindo venv e dados)
	@echo "$(YELLOW)⚠️  Removendo venv e dados...$(NC)"
	rm -rf .venv/ 2>/dev/null || true
	rm -rf *.egg-info/ 2>/dev/null || true
	rm -rf dist/ build/ 2>/dev/null || true
	rm -rf data/cache/* 2>/dev/null || true
	rm -rf logs/* 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza completa concluída!$(NC)"

# =============================================================================
# CI/CD
# =============================================================================

ci: check test ## 🔄 Executa pipeline de CI (lint + format + types + tests)
	@echo "$(GREEN)✅ Pipeline CI concluído com sucesso!$(NC)"

pre-commit: format lint type-check ## 🔒 Verificações pré-commit
	@echo "$(GREEN)✅ Pré-commit concluído!$(NC)"

# =============================================================================
# DEFAULT
# =============================================================================

.DEFAULT_GOAL := help

