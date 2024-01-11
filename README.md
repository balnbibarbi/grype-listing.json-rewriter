# Grype vulnerability database cache

Utility to ease offline use of Grype.
Downloads and caches an offline copy of the latest Grype vulnerability database.

## Configuration

| Setting name | Purpose | Default |
| ------------ | ------- | ------- |
| BASE_URL | Used to construct database URLs | / |
| SCHEME | Used to construct database URLs | http |
| HOSTNAME | Used to construct database URLs | localhost |
| PORT | Used to construct database URLs | 8080 |
| DB_URL_COMPONENT | Used to construct database URLs | /databases |
| UPSTREAM_LISTING_URL | URL for upstream listing.json | <https://toolbox-data.anchore.io/grype/databases/listing.json> |
| OUTPUT_DIR | Cache directory for listing and database files | /tmp |
| MINIMISE | If true, only cache the latest vulnerability database. If false, cache all versions. | true |

## Usage

### Running locally

First set environment variables as required above. Then execute:

```bash
./server.py
```

This will:

- Download the latest Grype vulnerability database listing
- Download the latest Grype vulnerability database referenced in the listing
- Output a modified vulnerability database listing, referencing only the latest vulnerability database
- Rewrite the URLs in the listing so they all begin with 'example.com'
- Serve the listing and database over the configured protocol, hostname and port

### Deploying to Kubernetes

Edit ```statefulset.yaml```.
Add HTTP_PROXY, REQUESTS_CA_BUNDLE etc environment variables, as required and as documented in the
[Python Requests documentation](https://docs.python-requests.org/en/latest/user/advanced/#proxies)
.

Set NAMESPACE (or set a current namespace in your kubectl context), then execute:

```bash
kubectl apply -f statefulset.yaml -n $NAMESPACE
```
