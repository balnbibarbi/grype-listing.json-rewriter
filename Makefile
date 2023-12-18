.PHONY: all
all: run

.PHONY: run
run: build
	docker run -i -e URLPREFIX=http://example.com/databases/ grype-listing.json-rewriter

.PHONY: build
build:
	docker build --progress=plain -t grype-listing.json-rewriter .
