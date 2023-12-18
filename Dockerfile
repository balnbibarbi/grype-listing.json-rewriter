FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD \
    ./rewriter.py \
    -i "${INPUT:--}" \
    -o "${OUTPUT:--}" \
    -u "$URLPREFIX" \
    -d "${DOWNLOAD_LATEST_DB}"
