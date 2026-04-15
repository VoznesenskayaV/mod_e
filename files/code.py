<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Анализ финансовых данных</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 92%;
            max-width: 1200px;
            margin: 30px auto;
        }

        .header {
            background: white;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            margin-bottom: 25px;
        }

        .header h1 {
            margin: 0 0 10px 0;
        }

        .header p {
            color: #444;
            line-height: 1.5;
            margin: 6px 0;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        .card h3 {
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #333;
        }

        .card p {
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            color: #2d6cdf;
        }

        .charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }

        .chart-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        }

        .table-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            margin-bottom: 25px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        table th, table td {
            border: 1px solid #dcdcdc;
            padding: 12px;
            text-align: center;
        }

        table th {
            background: #f0f3f7;
        }

        .buttons {
            margin-top: 20px;
        }

        .buttons a {
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
            padding: 10px 16px;
            background: #2d6cdf;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }

        .buttons a:hover {
            background: #1f4fa8;
        }

        .note {
            background: #eef4ff;
            border-left: 4px solid #2d6cdf;
            padding: 15px;
            border-radius: 6px;
            color: #333;
        }

        @media (max-width: 1000px) {
            .cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .charts {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 600px) {
            .cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">

        <div class="header">
            <h1>Система анализа финансовых данных</h1>
            <p>Приложение разработано на Python Flask с использованием MongoDB и Docker Compose.</p>
            <p>Ниже представлены результаты агрегации, графики финансовых данных и прогноз доходов на следующий квартал.</p>

            <div class="buttons">
                <a href="/aggregate" target="_blank">JSON агрегации</a>
                <a href="/forecast" target="_blank">JSON прогноза</a>
            </div>
        </div>

        <div class="cards">
            <div class="card">
                <h3>Общий доход</h3>
                <p>{{ aggregation.total_revenue }}</p>
            </div>
            <div class="card">
                <h3>Общие расходы</h3>
                <p>{{ aggregation.total_expenses }}</p>
            </div>
            <div class="card">
                <h3>Общая прибыль</h3>
                <p>{{ aggregation.total_profit }}</p>
            </div>
            <div class="card">
                <h3>Средний доход</h3>
                <p>{{ aggregation.average_revenue | round(2) }}</p>
            </div>
            <div class="card">
                <h3>Количество месяцев</h3>
                <p>{{ aggregation.months_count }}</p>
            </div>
        </div>

        <div class="charts">
            <div class="chart-box">
                <h2>Финансовые показатели по месяцам</h2>
                <canvas id="financeChart"></canvas>
            </div>

            <div class="chart-box">
                <h2>Прогноз доходов на следующий квартал</h2>
                <canvas id="forecastChart"></canvas>
            </div>
        </div>

        <div class="table-box">
            <h2>Исходные финансовые данные</h2>
            <table>
                <thead>
                    <tr>
                        <th>Месяц</th>
                        <th>Доход</th>
                        <th>Расходы</th>
                        <th>Прибыль</th>
                        <th>Категория</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in data %}
                    <tr>
                        <td>{{ item.month }}</td>
                        <td>{{ item.revenue }}</td>
                        <td>{{ item.expenses }}</td>
                        <td>{{ item.profit }}</td>
                        <td>{{ item.category }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="note">
            Прогноз рассчитан на основе среднего дохода за последние 3 месяца.
        </div>

    </div>

    <script>
        const months = {{ months | tojson }};
        const revenues = {{ revenues | tojson }};
        const expenses = {{ expenses | tojson }};
        const profits = {{ profits | tojson }};

        const forecastLabels = {{ forecast_labels | tojson }};
        const forecastValues = {{ forecast_values | tojson }};

        const financeCtx = document.getElementById('financeChart').getContext('2d');
        new Chart(financeCtx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Доход',
                        data: revenues,
                        backgroundColor: 'rgba(45, 108, 223, 0.7)'
                    },
                    {
                        label: 'Расходы',
                        data: expenses,
                        backgroundColor: 'rgba(220, 53, 69, 0.7)'
                    },
                    {
                        label: 'Прибыль',
                        data: profits,
                        backgroundColor: 'rgba(40, 167, 69, 0.7)'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });

        const forecastCtx = document.getElementById('forecastChart').getContext('2d');
        new Chart(forecastCtx, {
            type: 'line',
            data: {
                labels: forecastLabels,
                datasets: [
                    {
                        label: 'Прогноз дохода',
                        data: forecastValues,
                        borderColor: 'rgba(45, 108, 223, 1)',
                        backgroundColor: 'rgba(45, 108, 223, 0.2)',
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    </script>
</body>
</html>
