PROGRAM = 'fball-data-collector'
LABEL   = $(shell git rev-parse --abbrev-ref HEAD)

.PHONY: build

build:
	docker build -t $(PROGRAM):$(LABEL) .


