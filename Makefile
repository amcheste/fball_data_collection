build:
	docker build -t 'fball-data-database' -f db/Dockerfile .

create-vol:
	docker volume create 'database-vol' || true

remove-vol:
	docker volume rm 'database-vol' || true

start-db: create-vol
	docker run -it --rm \
		-e 'POSTGRES_PASSWORD=password' \
		-e 'POSTGRES_USER=user' \
		-e 'POSTGRES_DB=football' \
		-v 'database-vol:/var/lib/postgresql/data' \
		-p '5432:5432' \
		'fball-data-database'