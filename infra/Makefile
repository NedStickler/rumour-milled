ENV ?= local
AWS_REGION ?= eu-west-2
AWS_ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 000000000000)

ifeq ($(ENV),local)
	REGISTRY := localhost:5000
else
	REGISTRY := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
endif

IMAGES := rm-$(ENV)-scraper rm-$(ENV)-scrape-finish-handler

.PHONY: up down all

up:
	docker compose -f local/compose.yaml up -d

down:
	docker compose -f local/compose.yaml down -v

all: up
