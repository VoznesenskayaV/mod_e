const express = require('express');
const fs = require('fs');
const path = require('path');
const db = require('./config/db');

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const logDirPath = '/usr/src/app/logs';
const logFilePath = path.join(logDirPath, 'messages.log');

if (!fs.existsSync(logDirPath)) {
  fs.mkdirSync(logDirPath, { recursive: true });
}

function writeLog(text) {
  const logMessage = `[${new Date().toISOString()}] ${text}\n`;
  fs.appendFileSync(logFilePath, logMessage, 'utf8');
}

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/message', (req, res) => {
  const { client_name, message_text } = req.body;

  if (!client_name || !message_text) {
    return res.status(400).json({
      error: 'Поля client_name и message_text обязательны'
    });
  }

  const sql = 'INSERT INTO messages (client_name, message_text) VALUES (?, ?)';

  db.query(sql, [client_name, message_text], (err, result) => {
    if (err) {
      console.error('Ошибка при сохранении сообщения:', err.message);
      return res.status(500).json({
        error: 'Ошибка при сохранении сообщения'
      });
    }

    writeLog(`Клиент: ${client_name}, сообщение: ${message_text}`);

    res.status(201).json({
      message: 'Сообщение успешно сохранено',
      id: result.insertId,
      bot_reply: `Здравствуйте, ${client_name}! Ваше обращение принято в обработку.`
    });
  });
});

app.get('/stats', (req, res) => {
  const sql = `
    SELECT client_name, COUNT(*) AS request_count
    FROM messages
    GROUP BY client_name
    ORDER BY request_count DESC
  `;

  db.query(sql, (err, results) => {
    if (err) {
      console.error('Ошибка при получении статистики:', err.message);
      return res.status(500).json({
        error: 'Ошибка при получении статистики'
      });
    }

    res.json(results);
  });
});

db.query('SELECT 1', (err) => {
  if (err) {
    console.error('Ошибка подключения к MySQL:', err.message);
  } else {
    console.log('Подключение к MySQL успешно выполнено');
  }

  app.listen(PORT, () => {
    console.log(`Сервер запущен на порту ${PORT}`);
  });
});
