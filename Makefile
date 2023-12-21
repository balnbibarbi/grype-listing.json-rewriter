PROJECT_NAME=grype-listing.json-rewriter
DOCKER_HUB_USERNAME:=bingbangboo
LISTING_JSON_URL=https://toolbox-data.anchore.io/grype/databases/listing.json
OUTPUT_LISTING_JSON=/tmp/listing.json
NEW_URL_PREFIX=http://example.com/databases/
DB_OUTPUT_DIR=/tmp/
DOCKER_TAG=$(DOCKER_HUB_USERNAME)/$(PROJECT_NAME)
MINIMAL=true
VERBOSE=false
K8S_NS=grype-db
MAX_LB_IP_ATTEMPTS=10

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

.PHONY: k8s
k8s:
	if kubectl get ns "$(K8S_NS)" > /dev/null 2>&1 ; then true ; else kubectl create ns "$(K8S_NS)" ; fi
	kubectl apply -f statefulset.yaml -n "$(K8S_NS)"
	for attempt in `seq 1 "$(MAX_LB_IP_ATTEMPTS)"` ; do \
		ip=`kubectl get svc -n grype-db "$(K8S_NS)" -o=jsonpath='{.status.loadBalancer.ingress[0].ip}'`; \
		if test -n "$$ip" ; then \
			break ; \
		fi ; \
		sleep 5 ; \
	done ; \
	if test -z "$$ip" ; then \
		echo "No LoadBalancer IP after $(MAX_LB_IP_ATTEMPTS) attempts" ; \
		exit 1 ; \
	fi ; \
	curl --verbose --fail "http://$$ip/listing.json" \
	| jq -r '.available[][].url' \
	| sed -r -e "s/grype-db/$$ip/" \
	| xargs curl --verbose --fail --output /dev/null
	kubectl delete ns "$(K8S_NS)"
