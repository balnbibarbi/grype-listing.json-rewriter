.PHONY: all
all: run

.PHONY: run
run: build
	docker run -i \
		-e INPUT=https://toolbox-data.anchore.io/grype/databases/listing.json \
		-e OUTPUT=- \
		-e URLPREFIX=http://example.com/databases/ \
		-e DOWNLOAD_LATEST_DB=/tmp/ \
		-v "/tmp:/tmp" \
		grype-listing.json-rewriter

.PHONY: build
build:
	docker build --progress=plain -t grype-listing.json-rewriter .
