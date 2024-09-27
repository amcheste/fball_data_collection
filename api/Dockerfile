FROM docker.io/library/python:3.12.4-alpine3.20

WORKDIR /app

COPY requirements.txt .
RUN apk add gcc musl-dev libffi-dev g++ && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY app/ /app

EXPOSE 8080
WORKDIR /app

CMD ["fastapi", "run", "main.py"]