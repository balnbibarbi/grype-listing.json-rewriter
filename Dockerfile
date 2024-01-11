FROM python:3

STOPSIGNAL SIGINT
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ./server.py
