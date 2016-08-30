.PHONY: run, test

run: build
	docker-compose up

build:
	docker-compose build

test: build
	docker-compose run app python /src/app/tests.py
