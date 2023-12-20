FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD \
    ./rewriter.py \
    --input              "${LISTING_JSON_URL}" \
    --output             "${OUTPUT_LISTING_JSON}" \
    --url-prefix         "${NEW_URL_PREFIX}" \
    --download-latest-db "${DB_OUTPUT_DIR}" \
    --minimal            "${MINIMAL}"
