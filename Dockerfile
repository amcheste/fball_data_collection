FROM docker.io/library/python:3.12.4-alpine3.20

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY nfl_data.py /app
COPY collectors/ /app/collectors
COPY models/     /app/models



CMD ["python3", "nfl_data.py", "collect"]