FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY weather.py .

ENV PYTHONIOENCODING=utf-8

ENTRYPOINT ["python", "weather.py"]
