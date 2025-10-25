import os, requests, pandas as pd
from datetime import datetime


CITIES = {
    "London": {"lat": 51.5072, "lon": -0.1276},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917},
    }

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "weather_raw")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_weather(city, lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    w = r.json().get("current_weather", {})
    if not w:
        return None
    return {
        "city": city,
        "temperature": w["temperature"],
        "windspeed": w["windspeed"],
        "time": w["time"],
        "fetched_at": datetime.utcnow().isoformat()
        }

def save_csv(records):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(DATA_DIR, f"weather_{ts}.csv")
    pd.DataFrame(records).to_csv(out, index=False)
    print(f"Saved: {out}")

def main():

    all_records = []

    for c, loc in CITIES.items():
        rec = fetch_weather(c, loc["lat"], loc["lon"])
        if rec:
            all_records.append(rec)

    if all_records:
        save_csv(all_records)
    else:
        print("No data fetched")


if __name__ == "__main__":
    main()