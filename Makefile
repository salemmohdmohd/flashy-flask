SHELL := /bin/zsh

.PHONY: install backend frontend dev migrate seed

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r backend/requirements.txt

device:
	. .venv/bin/activate && flask --app backend.app run --debug

backend:
	. .venv/bin/activate && flask --app backend.app run --debug

migrate:
	. .venv/bin/activate && flask --app backend.app db upgrade

seed:
	. .venv/bin/activate && flask --app backend.app seed
