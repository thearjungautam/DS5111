default:
	@cat makefile

env:
	python3 -m venv env; . env/bin/activate; pip install --upgrade pip

update: env
	. env/bin/activate; pip install -r requirements.txt

lint:
	. env/bin/activate; pylint clean_ids.py

test: lint
	. env/bin/activate; pytest -vv tests
test_enrich:
	@. env/bin/activate && cat mock_transcripts.jsonl | python -u bin/enrich_transcripts.py | python bin/validate_schema.py

.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat data/enriched_transcripts.jsonl | env/bin/python3 bin/load_snowflake.py

# -----------------------------
# LAB08 Docker Pipeline
# -----------------------------

DOCKERHUB_USER := arjungautam00
DOCKER_IMAGE := $(DOCKERHUB_USER)/ds5111-pipeline:latest

.PHONY: docker-build docker-images docker-smoke docker-short-circuit \
	docker-load-snowflake docker-login docker-push docker-clean \
	docker-deploy docker-test

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-images:
	docker images

docker-smoke:
	cat data/youtube_ids.txt | docker run --rm -i $(DOCKER_IMAGE)

docker-short-circuit:
	cat data/youtube_ids.txt | docker run --rm -i --env-file .env \
		$(DOCKER_IMAGE) \
		bash -c "python bin/clean_ids.py | python bin/extract_transcripts_oop.py"

docker-load-snowflake:
	cat data/enriched_transcripts.jsonl | docker run --rm -i --env-file .env \
		$(DOCKER_IMAGE) \
		bash -c 'python bin/load_snowflake.py && echo "Docker Snowflake load completed successfully"'

docker-login:
	docker login

docker-push:
	docker push $(DOCKER_IMAGE)

docker-clean:
	docker ps -aq | xargs -r docker rm -f
	docker rmi $(DOCKER_IMAGE)

docker-deploy:
	cat data/enriched_transcripts.jsonl | docker run --rm -i --env-file .env \
		$(DOCKER_IMAGE) \
		bash -c 'python bin/load_snowflake.py && echo "Clean-room deployment completed successfully"'

docker-test:
	docker ps
	docker images
