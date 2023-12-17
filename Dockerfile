FROM python:3

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD /usr/bin/python3 rewriter.py -i - -o - -u "$URLPREFIX"
