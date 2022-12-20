include common/Makefile

all: format test

format: format-black format-isort

format-black:
	@echo [black] && poetry run black . -v
	#  --exclude "pnq\/__template__\.py" ".venv"

format-isort:
	@echo [isort] && poetry run isort --profile black --filter-files .

format-ruff:
	@echo [ruff] && poetry run ruff --fix --exclude .venv,working . || true

test:
	@echo [pytest] && poetry run pytest -sv -m "not slow" -x # x -１つエラーが発生したら中断する

