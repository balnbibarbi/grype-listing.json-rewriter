PROJECT_NAME=grype-listing.json-rewriter
DOCKER_HUB_USERNAME:=bingbangboo
LISTING_JSON_URL=https://toolbox-data.anchore.io/grype/databases/listing.json
OUTPUT_LISTING_JSON=/tmp/listing.json
NEW_URL_PREFIX=http://example.com/databases/
DB_OUTPUT_DIR=/tmp/
DOCKER_TAG=$(DOCKER_HUB_USERNAME)/$(PROJECT_NAME)

.PHONY: all
all: run

.PHONY: run
run: build
	docker run -i \
		-e "LISTING_JSON_URL=$(LISTING_JSON_URL)" \
		-e "OUTPUT_LISTING_JSON=$(OUTPUT_LISTING_JSON)" \
		-e "NEW_URL_PREFIX=$(NEW_URL_PREFIX)" \
		-e "DB_OUTPUT_DIR=$(DB_OUTPUT_DIR)" \
		-v "/tmp:/tmp" \
		"$(DOCKER_TAG)"

.PHONY: build
build:
	docker build --progress=plain -t "$(DOCKER_TAG)" .

.PHONY: push
push: build
	docker push "$(DOCKER_TAG)"

.PHONY: local
local:
	./rewriter.py \
	-i "$(LISTING_JSON_URL)" \
    -o "$(OUTPUT_LISTING_JSON)" \
    -u "$(NEW_URL_PREFIX)" \
    -d "$(DB_OUTPUT_DIR)"
