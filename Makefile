.PHONY: all
all: run

.PHONY: run
run: build
	cat listing.json | docker run -i -e URLPREFIX=http://example.com/databases/ grype-listing.json-rewriter

.PHONY: build
	docker build -t grype-listing.json-rewriter
