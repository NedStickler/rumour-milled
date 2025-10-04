SHELL := /usr/bin/env bash
ENV ?= local
AWS_REGION ?= eu-west-2
AWS_ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 000000000000)
images := scraper scrape_finish_handler
pytest_path ?= tests/


ifeq ($(ENV),local)
	registry := localhost:5000
else
	registry := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
endif

# TODO: Add ECR repo creation for non-local

.PHONY: test up down build all

test:
	(cd .. && pytest $(pytest_path))
up:
	docker compose -f local/compose.yaml up -d
down:
	docker compose -f local/compose.yaml down -v
build:
	@cd .. && for i in $(images); do \
		d=$${i//_/-}; \
		docker build \
			-f "services/$$i/Dockerfile" \
			-t "rm-$(ENV)-$$d:latest" \
			.; \
		docker tag \
			"rm-$(ENV)-$$d:latest" \
			"$(registry)/rumour-milled/rm-$(ENV)-$$d:latest"; \
		docker push \
			"$(registry)/rumour-milled/rm-$(ENV)-$$d:latest"; \
	done
all: up build
