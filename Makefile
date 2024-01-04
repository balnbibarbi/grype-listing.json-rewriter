PROJECT_NAME=grype-listing.json-rewriter
DOCKER_HUB_USERNAME:=bingbangboo
UPSTREAM_LISTING_URL=https://toolbox-data.anchore.io/grype/databases/listing.json
SCHEME=http
HOSTNAME=0.0.0.0
PORT=8080
OUTPUT_DIR=/tmp/
BASE_URL=/
DB_URL_COMPONENT=databases
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
		--publish "$(PORT):$(PORT)" \
		-e "BASE_URL=$(BASE_URL)" \
		-e "SCHEME=$(SCHEME)" \
		-e "HOSTNAME=$(HOSTNAME)" \
		-e "PORT=$(PORT)" \
		-e "DB_URL_COMPONENT=$(DB_URL_COMPONENT)" \
		-e "UPSTREAM_LISTING_URL=$(UPSTREAM_LISTING_URL)" \
		-e "OUTPUT_DIR=$(OUTPUT_DIR)" \
		-e "MINIMAL=$(MINIMAL)" \
		-e "VERBOSE=$(VERBOSE)" \
		-v "$(OUTPUT_DIR):$(OUTPUT_DIR)" \
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
	--input        "$(UPSTREAM_LISTING_URL)" \
	--minimal      "$(MINIMAL)" \
	--output       "$(OUTPUT_DIR)" \
	--base-url     "$(SCHEME)://$(HOSTNAME):$(PORT)$(BASE_URL)" \
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
	| sed -r -e "s/$(HOSTNAME):$(PORT)/$$ip/" \
	| xargs curl --verbose --fail --output /dev/null
	kubectl delete ns "$(K8S_NS)"
