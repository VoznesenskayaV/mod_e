from flask import Flask, jsonify
import pandas as pd
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__)

# Параметры подключения к InfluxDB
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "analytics_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "visits_bucket")

CSV_PATH = "/data/visits.csv"

def get_client():
    return InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )

@app.route("/")
def home():
    return jsonify({
        "message": "Visit Analytics API is running"
    })

@app.route("/load_data")
def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        client = get_client()
        write_api = client.write_api(write_options=SYNCHRONOUS)

        points = []
        for _, row in df.iterrows():
            point = (
                Point("visits")
                .tag("page", row["page"])
                .tag("source", row["source"])
                .field("user_id", int(row["user_id"]))
                .field("duration", int(row["duration"]))
                .time(row["timestamp"], WritePrecision.S)
            )
            points.append(point)

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)
        client.close()

        return jsonify({
            "status": "success",
            "message": f"{len(df)} records loaded into InfluxDB"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/visits")
def visits():
    try:
        df = pd.read_csv(CSV_PATH)
        return df.to_json(orient="records")
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/stats")
def stats():
    try:
        df = pd.read_csv(CSV_PATH)

        stats_result = {
            "total_visits": int(len(df)),
            "unique_users": int(df["user_id"].nunique()),
            "avg_duration": round(float(df["duration"].mean()), 2),
            "top_pages": df["page"].value_counts().to_dict(),
            "top_sources": df["source"].value_counts().to_dict()
        }

        return jsonify(stats_result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
