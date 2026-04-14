import os
import io
import base64

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, jsonify, render_template
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.linear_model import LinearRegression


app = Flask(__name__, template_folder="../templates")

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "supersecrettoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "attendance_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "attendance_bucket")

CSV_FILE = "/app/data/attendance_data.csv"


def get_client():
    return InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        timeout=30000
    )


def load_attendance_csv():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Файл не найден: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE)
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = pd.to_datetime(df["date"])
    df["present"] = df["present"].astype(int)
    return df


def write_data_to_influx(df):
    client = get_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch_size = 500
    points = []

    for _, row in df.iterrows():
        point = (
            Point("attendance")
            .tag("event_id", str(row["event_id"]))
            .tag("student_id", str(row["student_id"]))
            .tag("group", str(row["group"]))
            .tag("subject", str(row["subject"]))
            .field("present", int(row["present"]))
            .time(pd.to_datetime(row["time"]).to_pydatetime())
        )
        points.append(point)

        if len(points) >= batch_size:
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)
            points = []

    if points:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)

    client.close()


def query_attendance_data():
    client = get_client()
    query_api = client.query_api()

    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: 2024-09-01T00:00:00Z, stop: 2025-02-01T00:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "attendance")
      |> filter(fn: (r) => r["_field"] == "present")
    '''

    tables = query_api.query(query, org=INFLUX_ORG)

    records = []
    for table in tables:
        for record in table.records:
            records.append({
                "time": record.get_time(),
                "event_id": record.values.get("event_id"),
                "student_id": record.values.get("student_id"),
                "group": record.values.get("group"),
                "subject": record.values.get("subject"),
                "present": record.get_value()
            })

    client.close()

    if not records:
        return pd.DataFrame(columns=["time", "event_id", "student_id", "group", "subject", "present"])

    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = pd.to_datetime(df["time"].dt.date)
    df["present"] = df["present"].astype(int)
    return df.sort_values("time")


def prepare_daily_series(df):
    daily = df.groupby("date")["present"].mean().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")
    daily["rolling_mean"] = daily["present"].rolling(window=7, min_periods=1).mean()
    return daily


def build_plot(df):
    if df.empty:
        return None

    daily = prepare_daily_series(df)

    plt.figure(figsize=(11, 5))
    plt.plot(daily["date"], daily["present"], color="#9ecae1", linewidth=1.5, label="Дневная посещаемость")
    plt.plot(daily["date"], daily["rolling_mean"], color="#ff7f0e", linewidth=2.5, label="Скользящее среднее (7 дней)")
    plt.title("Посещаемость по дням")
    plt.xlabel("Дата")
    plt.ylabel("Средняя посещаемость")
    plt.ylim(0, 1.0)
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")


def build_forecast_plot(df):
    if df.empty:
        return None, None

    daily = prepare_daily_series(df)

    # Прогноз строим по сглаженному ряду, так он выглядит намного понятнее
    train_df = daily[["date", "rolling_mean"]].copy()
    train_df["day_num"] = np.arange(len(train_df))

    X = train_df[["day_num"]]
    y = train_df["rolling_mean"]

    model = LinearRegression()
    model.fit(X, y)

    future_days = 30
    last_day_num = int(train_df["day_num"].max())
    future_nums = np.arange(last_day_num + 1, last_day_num + future_days + 1)
    future_df = pd.DataFrame({"day_num": future_nums})
    future_pred = model.predict(future_df[["day_num"]])
    future_pred = np.clip(future_pred, 0, 1)

    last_date = train_df["date"].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days, freq="D")

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "forecast": future_pred
    })

    plt.figure(figsize=(11, 5))
    plt.plot(train_df["date"], train_df["rolling_mean"], color="#1f77b4", linewidth=2.5, label="Историческая посещаемость (7 дней)")
    plt.plot(forecast_df["date"], forecast_df["forecast"], color="#ff7f0e", linewidth=2.5, label="Прогноз на 30 дней")
    plt.title("Прогноз посещаемости на следующий месяц")
    plt.xlabel("Дата")
    plt.ylabel("Средняя посещаемость")
    plt.ylim(0, 1.0)
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    mean_forecast = round(float(forecast_df["forecast"].mean()), 3)

    return image_base64, mean_forecast


@app.route("/")
def index():
    df = query_attendance_data()

    total_records = len(df)
    avg_attendance = round(float(df["present"].mean()), 3) if not df.empty else 0.0

    plot_image = build_plot(df)
    forecast_image, mean_forecast = build_forecast_plot(df)

    group_stats = []
    subject_stats = []

    if not df.empty:
        temp_group = df.groupby("group")["present"].mean().reset_index().sort_values("group")
        for _, row in temp_group.iterrows():
            group_stats.append({
                "name": row["group"],
                "attendance": round(float(row["present"]), 3)
            })

        temp_subject = df.groupby("subject")["present"].mean().reset_index().sort_values("subject")
        for _, row in temp_subject.iterrows():
            subject_stats.append({
                "name": row["subject"],
                "attendance": round(float(row["present"]), 3)
            })

    return render_template(
        "index.html",
        total_records=total_records,
        avg_attendance=avg_attendance,
        group_stats=group_stats,
        subject_stats=subject_stats,
        plot_image=plot_image,
        forecast_image=forecast_image,
        mean_forecast=mean_forecast
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/generate")
def generate():
    df = load_attendance_csv()
    write_data_to_influx(df)
    return jsonify({
        "message": "Данные из CSV успешно загружены в InfluxDB",
        "records_written": int(len(df))
    })


@app.route("/stats")
def stats():
    df = query_attendance_data()

    if df.empty:
        return jsonify({"message": "Данных пока нет"})

    stats_data = {
        "total_records": int(len(df)),
        "average_attendance": round(float(df["present"].mean()), 3),
        "by_group": df.groupby("group")["present"].mean().round(3).to_dict(),
        "by_subject": df.groupby("subject")["present"].mean().round(3).to_dict()
    }

    return jsonify(stats_data)


@app.route("/forecast")
def forecast():
    df = query_attendance_data()

    if df.empty:
        return jsonify({"message": "Нет данных для прогноза"})

    _, mean_forecast = build_forecast_plot(df)

    return jsonify({
        "forecast_period": "next_30_days",
        "predicted_average_attendance": mean_forecast
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
