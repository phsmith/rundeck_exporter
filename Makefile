AUTHOR = phsmith
PROJECT = $(notdir $(PWD))
IMAGE_NAME = rundeck-exporter
IMAGE_VERSION = $(or ${VERSION}, latest)
DOCKER_IMAGE_TAG = $(AUTHOR)/$(IMAGE_NAME)
GHCR_IMAGE_TAG = ghcr.io/$(AUTHOR)/$(PROJECT)/$(IMAGE_NAME)

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
