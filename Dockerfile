FROM python:3.12-alpine

WORKDIR /app

COPY entrypoint.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/app/entrypoint.py"]
