PROJECT_NAME = $(notdir $(PWD))
VERSION = $(shell cat VERSION)

.SILENT: push

default: build

build:
	docker run --rm -i hadolint/hadolint:latest < Dockerfile

	docker build \
    	--rm \
		--network host \
    	--tag="$(PROJECT_NAME):$(VERSION)" \
    	--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
    	--build-arg VCS_REF=`git rev-parse --short HEAD` \
    	--build-arg VERSION="$(VERSION)" .

clean:
	docker rmi --force $(PROJECT_NAME):$(VERSION)

push:
	[ -z "$(git status --short --untracked-files=no)" ] && (echo -e "\nNeed to commit changes before push.\n"; exit 1)
	git tag -d latest
	git tag latest
	git push origin :latest
	git tag "v$(VERSION)"
	git push --all

debug:
    docker run --rm -it $(PROJECT_NAME):$(VERSION) /bin/sh

run:
    docker run --rm $(PROJECT_NAME):$(VERSION) \
		--host 0.0.0.0 \
		--rundeck.skip_ssl
