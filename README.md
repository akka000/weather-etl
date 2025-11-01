# Real-Time Weather Data Pipeline
**(Docker + Python + Airflow + PostgreSQL)**

A fully containerized data engineering project that fetches real-time weather data from the **Open-Meteo API**, stores it in **PostgreSQL**, and automates everything with **Apache Airflow** — all running in **Docker**.

## Overview

| Layer          | Tool                          | Purpose                              |
|----------------|-------------------------------|--------------------------------------|
| **Ingestion**  | Python + REST API (Open-Meteo)| Fetch live weather data              |
| **Storage**    | PostgreSQL                    | Store historical weather records     |
| **Orchestration** | Apache Airflow             | Schedule and monitor ETL jobs        |
| **Containerization** | Docker + Compose        | Consistent reproducible environment  |


## Setup Instructions

### Clone the repository

```bash
git clone https://github.com/akka000/weather-etl.git
cd weather-etl
```

### Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_USER=manra
POSTGRES_PASSWORD=manra
POSTGRES_DB=weatherdb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

AIRFLOW_EXECUTOR=SequentialExecutor
AIRFLOW_LOAD_EXAMPLES=False
AIRFLOW_USER=admin
AIRFLOW_FIRSTNAME=Arman
AIRFLOW_LASTNAME=Khaxar
AIRFLOW_EMAIL=admin@example.com
AIRFLOW_PASSWORD=admin
```

### Build and Run Containers

```bash
docker compose up -d --build
```

This launches:

- **Postgres** (database)
- **Airflow Webserver + Scheduler**
- **ETL service** (Python job container)
- **Airflow init** (first-time DB + user setup)

**Access the services:**

- **Airflow UI** → [http://localhost:8080](http://localhost:8080)

## ETL Script

**`etl/fetch_weather.py`**

Fetches weather for multiple cities using the **Open-Meteo API**, saves as CSV, and inserts into **PostgreSQL**.

**Key features:**
- Retries network calls
- Writes timestamped CSV to `/data/weather_raw/`
- Creates table `weather_data` automatically if missing

**Run manually (inside Docker):**

```bash
docker compose run --rm etl
```

## Airflow DAG

**`dags/weather_dag.py`**

Runs the ETL **every 10 minutes** using a simple `BashOperator`:

```python
fetch_weather = BashOperator(
    task_id="fetch_weather",
    bash_command="python /opt/airflow/etl/fetch_weather.py"
)
```

**Enable the DAG in the Airflow UI** → it will:

- Call ETL script **inside the Airflow container**
- Insert new data into **PostgreSQL** automatically

## Dockerfiles

### **`docker/Dockerfile.airflow`**

```dockerfile
FROM apache/airflow:2.11.0
USER airflow
COPY requirements_airflow.txt /tmp/requirements_airflow.txt
RUN pip install --no-cache-dir -r /tmp/requirements_airflow.txt
```

### **`docker/Dockerfile.etl`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_etl.txt /app/requirements_etl.txt
RUN pip install --no-cache-dir -r requirements_etl.txt
COPY etl/ etl/
COPY dags/ dags/
COPY data/ data/
COPY logs/ logs/
ENV PYTHONUNBUFFERED=1
CMD ["python3.11", "etl/fetch_weather.py"]
```

## Database Table

**Created automatically:**

```sql
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city TEXT,
    temperature FLOAT,
    windspeed FLOAT,
    time TIMESTAMP,
    fetched_at TIMESTAMP
);
```

**Check data:**

```bash
docker exec -it weather_postgres psql -U manra -d weatherdb -c "SELECT * FROM weather_data LIMIT 5;"
```


## End Result

- **Full ETL → DB → Airflow** workflow inside **Docker**
- **Weather data updates** automatically **every 10 minutes**
- **Data available** in **Postgres** for **BI/analytics**
- **One-command deployment**: `docker compose up -d --build`