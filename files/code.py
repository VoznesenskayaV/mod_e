<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Анализ финансовых данных</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 90%;
            max-width: 1100px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        }

        h1, h2 {
            color: #222;
        }

        p {
            color: #444;
            line-height: 1.5;
        }

        .buttons {
            margin: 20px 0 30px 0;
        }

        .buttons a {
            display: inline-block;
            margin-right: 12px;
            margin-bottom: 10px;
            padding: 12px 18px;
            background: #2d6cdf;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: 0.2s;
        }

        .buttons a:hover {
            background: #1f4fa8;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table th, table td {
            border: 1px solid #dcdcdc;
            padding: 12px;
            text-align: center;
        }

        table th {
            background: #f0f3f7;
        }

        .note {
            margin-top: 25px;
            padding: 15px;
            background: #eef4ff;
            border-left: 4px solid #2d6cdf;
            border-radius: 6px;
        }

        code {
            background: #f3f3f3;
            padding: 2px 6px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Система анализа финансовых данных</h1>
        <p>
            Веб-приложение разработано на <b>Python Flask</b> с использованием <b>MongoDB</b> в Docker-контейнерах.
        </p>
        <p>
            Приложение выполняет агрегацию финансовых данных и строит прогноз доходов на следующий квартал.
        </p>

        <div class="buttons">
            <a href="/aggregate" target="_blank">Открыть агрегацию данных</a>
            <a href="/forecast" target="_blank">Открыть прогноз доходов</a>
        </div>

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

        <div class="note">
            Для проверки API можно использовать маршруты:
            <code>/aggregate</code> и <code>/forecast</code>.
        </div>
    </div>
</body>
</html>
