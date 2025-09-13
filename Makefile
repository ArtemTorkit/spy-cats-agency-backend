.PHONY: setup run migrate superuser lint

setup:
	python -m venv venv
	venv\Scripts\python -m pip install --upgrade pip
	venv\Scripts\python -m pip install -r requirements.txt
	venv\Scripts\python manage.py makemigrations
	venv\Scripts\python manage.py migrate

run:
	venv\Scripts\python manage.py runserver

migrate:
	venv\Scripts\python manage.py makemigrations
	venv\Scripts\python manage.py migrate

superuser:
	venv\Scripts\python manage.py createsuperuser

lint:
	venv\Scripts\python -m flake8 . --exclude venv
