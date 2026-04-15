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


@app.route("/")
def home():
    collection = get_collection()
    data = list(collection.find({}, {"_id": 0}))
    return render_template("index.html", data=data)


@app.route("/aggregate")
def aggregate_data():
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
        return jsonify({"error": "Нет данных для агрегации"}), 404

    summary = result[0]
    summary.pop("_id", None)

    return jsonify({
        "aggregation_result": summary
    })


@app.route("/forecast")
def forecast():
    collection = get_collection()

    latest_data = list(
        collection.find({}, {"_id": 0, "month": 1, "revenue": 1})
        .sort("month", -1)
        .limit(3)
    )

    if len(latest_data) < 3:
        return jsonify({"error": "Недостаточно данных для прогноза. Нужно минимум 3 месяца."}), 400

    latest_data = list(reversed(latest_data))

    revenues = [item["revenue"] for item in latest_data]
    avg_revenue = sum(revenues) / len(revenues)

    forecast_data = {
        "next_quarter_forecast": {
            "month_1": round(avg_revenue, 2),
            "month_2": round(avg_revenue, 2),
            "month_3": round(avg_revenue, 2),
            "quarter_total": round(avg_revenue * 3, 2)
        },
        "based_on_last_3_months": latest_data
    }

    return jsonify(forecast_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
