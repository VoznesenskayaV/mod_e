from flask import Flask, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = "finance_db"
COLLECTION_NAME = "financial_data"


def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


def get_all_data():
    collection = get_collection()
    return list(collection.find({}, {"_id": 0}).sort("month", 1))


def get_aggregation():
    collection = get_collection()

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$revenue"},
                "total_expenses": {"$sum": "$expenses"},
                "total_profit": {"$sum": "$profit"},
                "average_revenue": {"$avg": "$revenue"},
                "months_count": {"$sum": 1}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    if not result:
        return None

    summary = result[0]
    summary.pop("_id", None)
    return summary


def get_forecast_data():
    collection = get_collection()

    latest_data = list(
        collection.find({}, {"_id": 0, "month": 1, "revenue": 1})
        .sort("month", -1)
        .limit(3)
    )

    if len(latest_data) < 3:
        return None

    latest_data = list(reversed(latest_data))
    revenues = [item["revenue"] for item in latest_data]
    avg_revenue = sum(revenues) / len(revenues)

    forecast = {
        "month_1": round(avg_revenue, 2),
        "month_2": round(avg_revenue, 2),
        "month_3": round(avg_revenue, 2),
        "quarter_total": round(avg_revenue * 3, 2)
    }

    return {
        "based_on_last_3_months": latest_data,
        "next_quarter_forecast": forecast
    }


@app.route("/")
def home():
    data = get_all_data()
    aggregation = get_aggregation()
    forecast_data = get_forecast_data()

    months = [item["month"] for item in data]
    revenues = [item["revenue"] for item in data]
    expenses = [item["expenses"] for item in data]
    profits = [item["profit"] for item in data]

    forecast_labels = ["Следующий месяц 1", "Следующий месяц 2", "Следующий месяц 3"]
    forecast_values = []

    if forecast_data:
        forecast_values = [
            forecast_data["next_quarter_forecast"]["month_1"],
            forecast_data["next_quarter_forecast"]["month_2"],
            forecast_data["next_quarter_forecast"]["month_3"]
        ]

    return render_template(
        "index.html",
        data=data,
        aggregation=aggregation,
        forecast_data=forecast_data,
        months=months,
        revenues=revenues,
        expenses=expenses,
        profits=profits,
        forecast_labels=forecast_labels,
        forecast_values=forecast_values
    )


@app.route("/aggregate")
def aggregate_data():
    summary = get_aggregation()

    if not summary:
        return jsonify({"error": "Нет данных для агрегации"}), 404

    return jsonify({
        "aggregation_result": summary
    })


@app.route("/forecast")
def forecast():
    forecast_data = get_forecast_data()

    if not forecast_data:
        return jsonify({"error": "Недостаточно данных для прогноза. Нужно минимум 3 месяца."}), 400

    return jsonify(forecast_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
