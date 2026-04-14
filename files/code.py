import os
import io
import base64
from datetime import datetime, timedelta

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


def get_client():
    return InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        timeout=30000
    )


def generate_attendance_data(n_records=1200):
    np.random.seed(42)

    groups = ["A-101", "A-102", "B-201", "B-202"]
    subjects = ["Math", "Physics", "Informatics", "Statistics"]
    student_ids = [f"S{i:03d}" for i in range(1, 81)]

    current_date = datetime.now() - timedelta(days=180)
    rows = []
    event_id = 1

    while len(rows) < n_records:
        if current_date.weekday() < 5:
            records_today = np.random.randint(5, 11)

            for i in range(records_today):
                if len(rows) >= n_records:
                    break

                student_id = np.random.choice(student_ids)
                group = np.random.choice(groups)
                subject = np.random.choice(subjects)

                base_attendance = {
                    "A-101": 0.90,
                    "A-102": 0.85,
                    "B-201": 0.80,
                    "B-202": 0.75
                }[group]

                month_factor = 0.0
                if current_date.month in [12, 5]:
                    month_factor = -0.08
                elif current_date.month in [2, 3, 10]:
                    month_factor = 0.03

                subject_factor = {
                    "Math": -0.03,
                    "Physics": -0.05,
                    "Informatics": 0.02,
                    "Statistics": -0.01
                }[subject]

                prob_present = max(0.55, min(0.98, base_attendance + month_factor + subject_factor))
                present = int(np.random.rand() < prob_present)

                event_time = current_date + timedelta(
                    hours=8 + (i % 8),
                    minutes=np.random.randint(0, 60),
                    seconds=np.random.randint(0, 60),
                    microseconds=event_id
                )

                rows.append({
                    "time": event_time,
                    "event_id": f"E{event_id:06d}",
                    "student_id": student_id,
                    "group": group,
                    "subject": subject,
                    "present": present
                })

                event_id += 1

        current_date += timedelta(days=1)

    return pd.DataFrame(rows)


def write_data_to_influx(df):
    client = get_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    batch_size = 200
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
      |> range(start: -365d)
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
    df["date"] = df["time"].dt.date
    return df


def build_plot(df):
    if df.empty:
        return None

    daily = df.groupby("date")["present"].mean().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")

    daily["rolling_mean"] = daily["present"].rolling(window=7, min_periods=1).mean()

    plt.figure(figsize=(11, 5))
    plt.plot(daily["date"], daily["present"], alpha=0.35, label="Дневная посещаемость")
    plt.plot(daily["date"], daily["rolling_mean"], linewidth=2.5, label="Скользящее среднее (7 дней)")
    plt.title("Посещаемость по дням")
    plt.xlabel("Дата")
    plt.ylabel("Средняя посещаемость")
    plt.ylim(0, 1.05)
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

    daily = df.groupby("date")["present"].mean().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")

    daily["day_num"] = np.arange(len(daily))

    X = daily[["day_num"]]
    y = daily["present"]

    model = LinearRegression()
    model.fit(X, y)

    future_days = 30
    last_day_num = int(daily["day_num"].max())
    future_nums = np.arange(last_day_num + 1, last_day_num + future_days + 1)
    future_df = pd.DataFrame({"day_num": future_nums})
    future_pred = model.predict(future_df[["day_num"]])
    future_pred = np.clip(future_pred, 0, 1)

    last_date = daily["date"].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, future_days + 1)]

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "forecast": future_pred
    })

    daily["rolling_mean"] = daily["present"].rolling(window=7, min_periods=1).mean()

    plt.figure(figsize=(11, 5))
    plt.plot(daily["date"], daily["rolling_mean"], linewidth=2.5, label="Историческая посещаемость (7 дней)")
    plt.plot(forecast_df["date"], forecast_df["forecast"], linewidth=2.5, label="Прогноз на 30 дней")
    plt.title("Прогноз посещаемости на следующий месяц")
    plt.xlabel("Дата")
    plt.ylabel("Средняя посещаемость")
    plt.ylim(0, 1.05)
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
        temp_group = df.groupby("group")["present"].mean().reset_index()
        for _, row in temp_group.iterrows():
            group_stats.append({
                "name": row["group"],
                "attendance": round(float(row["present"]), 3)
            })

        temp_subject = df.groupby("subject")["present"].mean().reset_index()
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
    df = generate_attendance_data(n_records=1200)
    write_data_to_influx(df)
    return jsonify({
        "message": "Данные успешно сгенерированы и записаны в InfluxDB",
        "records_written": len(df)
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
