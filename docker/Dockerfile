FROM python:3.11-slim
WORKDIR /app
COPY docker/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY etl/ etl/
COPY dags/ dags/
COPY data/ data/
COPY logs/ logs/
ENV PYTHONUNBUFFERED=1
CMD ["python3.11", "etl/fetch_weather.py"]