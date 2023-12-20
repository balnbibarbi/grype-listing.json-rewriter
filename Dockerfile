FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD \
    ./rewriter.py \
    --download-dbs "${DB_OUTPUT_DIR}" \
    --input        "${LISTING_JSON_URL}" \
    --minimal      "${MINIMAL}" \
    --output       "${OUTPUT_LISTING_JSON}" \
    --url-prefix   "${NEW_URL_PREFIX}" \
    --verbose      "${VERBOSE}"
