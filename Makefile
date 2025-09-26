SHELL := /bin/zsh

VENV := .venv

.PHONY: install backend frontend dev migrate seed lint-backend lint-frontend test clean makemigration

install:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -r backend/requirements.txt
	npm install
	npm install --prefix frontend

backend:
	. $(VENV)/bin/activate && flask --app backend.app run --debug --port 5000

frontend:
	npm run start --prefix frontend

dev:
	npm run dev

migrate:
	. $(VENV)/bin/activate && flask --app backend.app db upgrade

seed:
	. $(VENV)/bin/activate && flask --app backend.app seed

makemigration:
	@if [ -z "$(message)" ]; then \
		echo "Usage: make makemigration message='describe change'"; exit 1; \
	fi
	. $(VENV)/bin/activate && flask --app backend.app db migrate -m "$(message)"

lint-backend:
	. $(VENV)/bin/activate && flake8 backend

lint-frontend:
	npm run lint --prefix frontend

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf $(VENV) backend/__pycache__ backend/app/__pycache__ frontend/node_modules
