<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Чат-бот поддержки клиентов</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <h1>Чат-бот поддержки клиентов</h1>
    <p class="subtitle">Отправка обращения клиента</p>

    <form id="messageForm">
      <label for="client_name">Имя клиента</label>
      <input type="text" id="client_name" name="client_name" placeholder="Введите имя" required />

      <label for="message_text">Сообщение</label>
      <textarea id="message_text" name="message_text" placeholder="Введите обращение" required></textarea>

      <button type="submit">Отправить сообщение</button>
    </form>

    <div id="responseBlock" class="card hidden">
      <h2>Ответ системы</h2>
      <p id="responseText"></p>
    </div>

    <div class="stats-section">
      <button id="loadStatsBtn">Показать статистику обращений</button>

      <div id="statsBlock" class="card hidden">
        <h2>Статистика обращений</h2>
        <table>
          <thead>
            <tr>
              <th>Клиент</th>
              <th>Количество обращений</th>
            </tr>
          </thead>
          <tbody id="statsTableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script src="script.js"></script>
</body>
</html>
