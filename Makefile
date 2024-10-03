

.PHONY: start stop logs

start:
	docker compose up --build --wait

logs:
	docker compose logs

stop:
	docker compose down --volumes