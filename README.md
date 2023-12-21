# Grype DB downloader

Utility to ease offline use of Grype.

## Usage

```bash
./rewriter.py \
        --download-dbs "/tmp/" \
        --input        "https://toolbox-data.anchore.io/grype/databases/listing.json" \
        --minimal      "true" \
        --output       "/tmp/listing.json" \
        --url-prefix   "http://example.com/databases/" \
        --verbose      "false"
```

This will:

- Download the latest Grype vulnerability database listing
- Download the latest Grype vulnerability database referenced in the listing
- Output a modified vulnerability database listing, referencing only the latest vulnerability database
- Rewrite the URLs in the listing so they all begin with 'example.com'
