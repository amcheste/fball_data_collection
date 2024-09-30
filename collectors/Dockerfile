FROM docker.io/library/python:3.12.4-alpine3.20

COPY requirements.txt .
RUN apk add gcc musl-dev libffi-dev g++ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY app/ /app
COPY main.py .

CMD ["python3", "main.py"]