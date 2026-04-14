<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Система анализа посещаемости</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background: #f4f6f8;
            color: #222;
        }

        h1 {
            margin-top: 0;
            font-size: 42px;
        }

        h2 {
            margin-top: 0;
            font-size: 26px;
        }

        .card {
            background: #ffffff;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        }

        .metrics {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .metric-box {
            flex: 1;
            min-width: 220px;
            background: #f9fafb;
            border-radius: 10px;
            padding: 18px;
            border: 1px solid #e5e7eb;
        }

        .metric-title {
            font-size: 15px;
            color: #555;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }

        .tables {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }

        .table-box {
            flex: 1;
            min-width: 320px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            border: 1px solid #dcdcdc;
            padding: 10px 12px;
            text-align: left;
        }

        th {
            background: #f3f4f6;
        }

        img {
            max-width: 100%;
            border-radius: 8px;
            border: 1px solid #ddd;
            background: white;
        }

        .note {
            color: #555;
            font-size: 15px;
            margin-top: 6px;
        }
    </style>
</head>
<body>
    <h1>Система анализа посещаемости</h1>

    <div class="card">
        <div class="metrics">
            <div class="metric-box">
                <div class="metric-title">Количество записей</div>
                <div class="metric-value">{{ total_records }}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Средняя посещаемость</div>
                <div class="metric-value">{{ avg_attendance }}</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Прогноз на следующий месяц</div>
                <div class="metric-value">
                    {% if mean_forecast is not none %}
                        {{ mean_forecast }}
                    {% else %}
                        —
                    {% endif %}
                </div>
            </div>
        </div>
        <div class="note">
            На странице показаны агрегированные данные по посещаемости и прогноз на следующие 30 дней.
        </div>
    </div>

    <div class="card">
        <h2>Сводная статистика</h2>
        <div class="tables">
            <div class="table-box">
                <h3>По группам</h3>
                <table>
                    <tr>
                        <th>Группа</th>
                        <th>Средняя посещаемость</th>
                    </tr>
                    {% for row in group_stats %}
                    <tr>
                        <td>{{ row.name }}</td>
                        <td>{{ row.attendance }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            <div class="table-box">
                <h3>По предметам</h3>
                <table>
                    <tr>
                        <th>Предмет</th>
                        <th>Средняя посещаемость</th>
                    </tr>
                    {% for row in subject_stats %}
                    <tr>
                        <td>{{ row.name }}</td>
                        <td>{{ row.attendance }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>График посещаемости</h2>
        {% if plot_image %}
            <img src="data:image/png;base64,{{ plot_image }}" alt="График посещаемости">
        {% else %}
            <p>Пока нет данных для построения графика.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Прогноз на следующий месяц</h2>
        {% if forecast_image %}
            <img src="data:image/png;base64,{{ forecast_image }}" alt="Прогноз посещаемости">
        {% else %}
            <p>Пока нет данных для прогноза.</p>
        {% endif %}
    </div>
</body>
</html>
