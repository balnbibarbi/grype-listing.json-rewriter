LISTING_URL=https://toolbox-data.anchore.io/grype/databases/listing.json
OUTPUT=/tmp/listing.json
URLPREFIX=http://example.com/databases/
DOWNLOAD_LATEST_DB=/tmp/

.PHONY: all
all: run

.PHONY: run
run: build
	docker run -i \
		-e INPUT=$(LISTING_URL) \
		-e OUTPUT=$(OUTPUT) \
		-e URLPREFIX=$(URLPREFIX) \
		-e DOWNLOAD_LATEST_DB=$(DOWNLOAD_LATEST_DB) \
		-v "/tmp:/tmp" \
		grype-listing.json-rewriter

.PHONY: build
build:
	docker build --progress=plain -t grype-listing.json-rewriter .

.PHONY: local
local:
	./rewriter.py \
	-i "$(LISTING_URL)" \
    -o "$(OUTPUT)" \
    -u "$(URLPREFIX)" \
    -d "$(DOWNLOAD_LATEST_DB)"
