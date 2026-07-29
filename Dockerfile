FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY bin/ ./bin/

RUN mkdir -p pipeline/logs

CMD ["sh", "-c", "python bin/clean_ids.py"]
