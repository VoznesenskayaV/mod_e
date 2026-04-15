<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система прогнозирования спроса</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #1f2937;
        }

        .container {
            width: 90%;
            max-width: 1200px;
            margin: 30px auto;
        }

        .header {
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            color: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }

        .header h1 {
            margin: 0 0 10px 0;
            font-size: 32px;
        }

        .header p {
            margin: 0;
            font-size: 16px;
            opacity: 0.95;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        }

        .card h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #6b7280;
        }

        .card .value {
            font-size: 32px;
            font-weight: bold;
            color: #111827;
        }

        .section {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            margin-bottom: 25px;
        }

        .section h2 {
            margin-top: 0;
            margin-bottom: 18px;
            font-size: 24px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 12px;
        }

        thead {
            background: #2563eb;
            color: white;
        }

        th, td {
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        tbody tr:hover {
            background: #f9fafb;
        }

        .analytics-list {
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .analytics-list li {
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
            font-size: 16px;
        }

        .analytics-list li:last-child {
            border-bottom: none;
        }

        .badge {
            display: inline-block;
            padding: 6px 10px;
            background: #dbeafe;
            color: #1d4ed8;
            border-radius: 999px;
            font-size: 13px;
            font-weight: bold;
        }

        .chart-container {
            position: relative;
            height: 420px;
        }

        .footer {
            text-align: center;
            color: #6b7280;
            margin: 20px 0 40px;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 24px;
            }

            .card .value {
                font-size: 26px;
            }

            th, td {
                padding: 10px 12px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Система прогнозирования спроса</h1>
            <p>Аналитическая панель по товарам и среднему спросу по категориям</p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Всего товаров</h3>
                <div class="value">{{ total_products }}</div>
            </div>

            <div class="card">
                <h3>Количество категорий</h3>
                <div class="value">{{ total_categories }}</div>
            </div>

            <div class="card">
                <h3>Максимальный спрос</h3>
                <div class="value">{{ max_demand }}</div>
            </div>

            <div class="card">
                <h3>Средний спрос по всем товарам</h3>
                <div class="value">{{ overall_avg }}</div>
            </div>
        </div>

        <div class="section">
            <h2>Таблица товаров</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Название товара</th>
                        <th>Категория</th>
                        <th>Спрос</th>
                    </tr>
                </thead>
                <tbody>
                    {% for product in products %}
                    <tr>
                        <td>{{ product.id }}</td>
                        <td>{{ product.product_name }}</td>
                        <td><span class="badge">{{ product.category }}</span></td>
                        <td>{{ product.demand_value }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Средний спрос по категориям</h2>
            <ul class="analytics-list">
                {% for item in averages %}
                <li>
                    <strong>{{ item.category }}</strong> — средний спрос: <strong>{{ item.average_demand }}</strong>
                </li>
                {% endfor %}
            </ul>
        </div>

        <div class="section">
            <h2>График среднего спроса по категориям</h2>
            <div class="chart-container">
                <canvas id="demandChart"></canvas>
            </div>
        </div>

        <div class="footer">
            Отчетная аналитическая панель для задания по Docker, Flask и PostgreSQL
        </div>
    </div>

    <script>
        const categoryLabels = {{ chart_labels | tojson }};
        const categoryValues = {{ chart_values | tojson }};

        const ctx = document.getElementById('demandChart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categoryLabels,
                datasets: [{
                    label: 'Средний спрос',
                    data: categoryValues,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: 'Средний спрос по категориям товаров'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
