include common/Makefile

format-ruff:
	@echo [ruff] && poetry run ruff --fix --exclude .venv,working . || true
