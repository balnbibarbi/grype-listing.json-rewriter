FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD \
    ./rewriter.py \
    -i "${LISTING_JSON_URL}" \
    -o "${OUTPUT_LISTING_JSON}" \
    -u "${NEW_URL_PREFIX}" \
    -d "${DB_OUTPUT_DIR}"
