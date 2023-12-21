PROJECT_NAME=grype-listing.json-rewriter
DOCKER_HUB_USERNAME:=bingbangboo
LISTING_JSON_URL=https://toolbox-data.anchore.io/grype/databases/listing.json
OUTPUT_LISTING_JSON=/tmp/listing.json
NEW_URL_PREFIX=http://example.com/databases/
DB_OUTPUT_DIR=/tmp/
DOCKER_TAG=$(DOCKER_HUB_USERNAME)/$(PROJECT_NAME)
MINIMAL=true
VERBOSE=false

.PHONY: all
all: test local run

.PHONY: run
run: build
	docker run -i \
		-e "DB_OUTPUT_DIR=$(DB_OUTPUT_DIR)" \
		-e "LISTING_JSON_URL=$(LISTING_JSON_URL)" \
		-e "MINIMAL=$(MINIMAL)" \
		-e "OUTPUT_LISTING_JSON=$(OUTPUT_LISTING_JSON)" \
		-e "NEW_URL_PREFIX=$(NEW_URL_PREFIX)" \
		-e "VERBOSE=$(VERBOSE)" \
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
	--download-dbs "$(DB_OUTPUT_DIR)" \
	--input        "$(LISTING_JSON_URL)" \
	--minimal      "$(MINIMAL)" \
	--output       "$(OUTPUT_LISTING_JSON)" \
	--url-prefix   "$(NEW_URL_PREFIX)" \
	--verbose      "$(VERBOSE)"

.PHONY: test
test:
	./tests.py
