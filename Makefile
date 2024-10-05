

.PHONY: start stop logs

start:
	docker compose up --build --wait

logs:
	docker compose logs

stop:
	docker compose down --volumes


discover:
	python3 nfl_data.py discover --type=positions
	python3 nfl_data.py discover --type=teams --start=2024 --end=2024
	python3 nfl_data.py discover --type=players --start=2024 --end=2024

collect:
	python3 nfl_data.py collect --type=positions
	python3 nfl_data.py collect --type=teams
	python3 nfl_data.py collect --type=players