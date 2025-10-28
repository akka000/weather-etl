import os, requests, pandas as pd
from datetime import datetime
import psycopg2

CITIES = {
    "London": {"lat": 51.5072, "lon": -0.1276},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917},
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data", "weather_raw")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_weather(city, lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        current = resp.json().get("current_weather", {})
        if not current:
            print(f"No data for {city}")
            return None
        return {
            "city": city,
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "time": current.get("time"),
            "fetched_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error fetching {city}: {e}")
        return None

def save_csv(records):
    if not records:
        print("No records to save.")
        return
    df = pd.DataFrame(records)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DATA_DIR, f"weather_{ts}.csv")
    df.to_csv(path, index=False)
    print(f"Saved CSV: {path}")

def save_to_postgres(records):
    if not records:
        print("No records to insert.")
        return
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "weatherdb"),
            user=os.getenv("POSTGRES_USER", "manra"),
            password=os.getenv("POSTGRES_PASSWORD", "manra"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port="5432",
        )
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city TEXT,
            temperature FLOAT,
            windspeed FLOAT,
            time TIMESTAMP,
            fetched_at TIMESTAMP
        );""")
        for r in records:
            cur.execute("""
                INSERT INTO weather_data (city, temperature, windspeed, time, fetched_at)
                VALUES (%s,%s,%s,%s,%s);
            """, (r["city"], r["temperature"], r["windspeed"], r["time"], r["fetched_at"]))
        conn.commit()
        cur.close()
        conn.close()
        print("Inserted data into Postgres.")
    except Exception as e:
        print(f"Database error: {e}")

def main():
    all_records = []
    for city, loc in CITIES.items():
        rec = fetch_weather(city, loc["lat"], loc["lon"])
        if rec:
            all_records.append(rec)
    save_csv(all_records)
    save_to_postgres(all_records)

if __name__ == "__main__":
    main()
