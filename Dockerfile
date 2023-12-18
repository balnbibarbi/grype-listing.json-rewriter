FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ./rewriter.py -i "${INPUT:-https://toolbox-data.anchore.io/grype/databases/listing.json}" -o "${OUTPUT:--}" -u "$URLPREFIX"
