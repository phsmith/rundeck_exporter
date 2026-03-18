AUTHOR = phsmith
PROJECT = $(notdir $(PWD))
IMAGE_NAME ?= rundeck-exporter
IMAGE_VERSION ?= latest
DOCKER_IMAGE_TAG = $(AUTHOR)/$(IMAGE_NAME)
GHCR_IMAGE_TAG = ghcr.io/$(AUTHOR)/$(PROJECT)/$(IMAGE_NAME)

RD_CLI_VERSION = 2.0.9
RD_CLI_JAR = rundeck-cli-$(RD_CLI_VERSION)-all.jar
RD_CLI_URL = https://github.com/rundeck/rundeck-cli/releases/download/v$(RD_CLI_VERSION)/$(RD_CLI_JAR)
CI_COMPOSE = examples/docker-compose/docker-compose-ci.yml

default: docker-build

docker-build:
	docker run --rm -i hadolint/hadolint:latest < Dockerfile

	docker pull $(GHCR_IMAGE_TAG) || true

	DOCKER_BUILDKIT=1 docker build \
		--cache-from=$(GHCR_IMAGE_TAG) \
		--cache-from=$(DOCKER_IMAGE_TAG) \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
    	--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    	--build-arg VCS_REF=`git rev-parse --short HEAD` \
    	--build-arg VERSION="$(IMAGE_VERSION)" \
		--target app \
    	--tag=$(IMAGE_NAME) .

	docker tag $(IMAGE_NAME) $(DOCKER_IMAGE_TAG):latest
	docker tag $(IMAGE_NAME) $(GHCR_IMAGE_TAG):latest
	docker tag $(IMAGE_NAME) $(DOCKER_IMAGE_TAG):$(IMAGE_VERSION)
	docker tag $(IMAGE_NAME) $(GHCR_IMAGE_TAG):$(IMAGE_VERSION)

docker-push:
	@echo "$(DOCKER_HUB_TOKEN)" | docker login -u $(AUTHOR) --password-stdin
	docker push $(DOCKER_IMAGE_TAG):$(IMAGE_VERSION)

ghcr-push:
	@echo "$(GITHUB_TOKEN)" | docker login ghcr.io -u $(AUTHOR) --password-stdin
	docker push $(GHCR_IMAGE_TAG):$(IMAGE_VERSION)

push-all:
	make -j2 docker-push ghcr-push

clean:
	@docker rmi --force `docker images | awk '/$(IMAGE_NAME)/ {print $3}'` &> /dev/null || true
	@echo "> Project Docker images cleaned up."

git-push:
	[ -z "$(git status --short --untracked-files=no)" ] && (echo -e "\nNeed to commit changes before push.\n"; exit 1)
	git tag -d latest
	git tag latest
	git push origin :latest
	git tag "v$(IMAGE_VERSION)"
	git push --all

debug:
	docker run --rm -it --name=$(IMAGE_NAME) --entrypoint=/bin/sh $(IMAGE_NAME)

docker-compose-up:
	docker compose -f examples/docker-compose/docker-compose.yml up --build -d

docker-compose-down:
	docker compose -f examples/docker-compose/docker-compose.yml down

docker-compose-logs:
	docker compose -f examples/docker-compose/docker-compose.yml logs $(ARGS)

test-setup:
	docker compose -f $(CI_COMPOSE) up -d --wait
	curl -L -o /tmp/rd-cli.jar $(RD_CLI_URL)
	docker compose -f $(CI_COMPOSE) cp /tmp/rd-cli.jar rundeck:/tmp/
	docker compose -f $(CI_COMPOSE) cp examples/docker-compose/configs/rundeck/projects/test1.rdproject.jar rundeck:/tmp/
	docker compose -f $(CI_COMPOSE) exec \
		-e RD_URL=http://localhost:4440 \
		-e RD_TOKEN=exporter_admin_auth_token \
		rundeck /bin/bash -c "cd /tmp \
			&& java -jar rd-cli.jar projects create -p test1 || true \
			&& java -jar rd-cli.jar projects archives import -p test1 -f test1.rdproject.jar"
	@echo "> Waiting for Rundeck API to be ready..."
	@for i in $$(seq 1 30); do \
		if curl -sf http://localhost:4440/api/41/system/info \
			-H "X-Rundeck-Auth-Token: exporter_admin_auth_token" > /dev/null 2>&1; then \
			echo "Rundeck API is ready."; break; \
		fi; \
		echo "Attempt $$i/30 - not ready, retrying in 5s..."; \
		sleep 5; \
	done
	@echo "> Waiting for scheduled job executions to complete..."
	@sleep 30

test-setup-logs:
	docker compose -f $(CI_COMPOSE) logs $(ARGS)

test:
	uv run pytest

test-teardown:
	docker compose -f $(CI_COMPOSE) down --volumes
