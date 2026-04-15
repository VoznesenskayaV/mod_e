document.addEventListener('DOMContentLoaded', () => {
  const checkServerBtn = document.getElementById('checkServerBtn');
  const serverStatus = document.getElementById('serverStatus');

  const checkDbBtn = document.getElementById('checkDbBtn');
  const dbStatus = document.getElementById('dbStatus');

  const loadSalesBtn = document.getElementById('loadSalesBtn');
  const salesContainer = document.getElementById('salesContainer');

  const loadSummaryBtn = document.getElementById('loadSummaryBtn');
  const summaryContainer = document.getElementById('summaryContainer');

  const loadMonthlyBtn = document.getElementById('loadMonthlyBtn');
  const monthlyContainer = document.getElementById('monthlyContainer');
  const reportYear = document.getElementById('reportYear');
  const reportMonth = document.getElementById('reportMonth');

  checkServerBtn.addEventListener('click', async () => {
    serverStatus.textContent = 'Проверка сервера...';

    try {
      const response = await fetch('/api/health');
      const data = await response.json();

      serverStatus.innerHTML = `
        <strong>Статус:</strong> ${data.message}<br>
        <strong>Успех:</strong> ${data.success}<br>
        <strong>Время:</strong> ${new Date(data.timestamp).toLocaleString()}
      `;
    } catch (error) {
      serverStatus.innerHTML = `<strong>Ошибка:</strong> сервер недоступен`;
    }
  });

  checkDbBtn.addEventListener('click', async () => {
    dbStatus.textContent = 'Проверка базы данных...';

    try {
      const response = await fetch('/api/db-status');
      const data = await response.json();

      dbStatus.innerHTML = `
        <strong>Статус базы:</strong> ${data.databaseStatus}
      `;
    } catch (error) {
      dbStatus.innerHTML = `<strong>Ошибка:</strong> база недоступна`;
    }
  });

  loadSalesBtn.addEventListener('click', async () => {
    salesContainer.textContent = 'Загрузка продаж...';

    try {
      const response = await fetch('/api/sales');
      const data = await response.json();

      if (!data.sales || data.sales.length === 0) {
        salesContainer.innerHTML = 'Продажи не найдены';
        return;
      }

      let tableHtml = `
        <table>
          <thead>
            <tr>
              <th>Товар</th>
              <th>Категория</th>
              <th>Количество</th>
              <th>Цена</th>
              <th>Сумма</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
      `;

      data.sales.forEach((sale) => {
        tableHtml += `
          <tr>
            <td>${sale.productName}</td>
            <td>${sale.category}</td>
            <td>${sale.quantity}</td>
            <td>${sale.price}</td>
            <td>${sale.totalAmount}</td>
            <td>${new Date(sale.saleDate).toLocaleDateString()}</td>
          </tr>
        `;
      });

      tableHtml += `
          </tbody>
        </table>
      `;

      salesContainer.innerHTML = tableHtml;
    } catch (error) {
      salesContainer.innerHTML = `<strong>Ошибка:</strong> не удалось загрузить продажи`;
    }
  });

  loadSummaryBtn.addEventListener('click', async () => {
    summaryContainer.textContent = 'Загрузка общей статистики...';

    try {
      const response = await fetch('/api/stats/summary');
      const data = await response.json();

      summaryContainer.innerHTML = `
        <div class="stat-item"><strong>Количество продаж:</strong> ${data.totalSalesCount}</div>
        <div class="stat-item"><strong>Общая выручка:</strong> ${data.totalRevenue}</div>
        <div class="stat-item"><strong>Средний чек:</strong> ${data.averageCheck.toFixed(2)}</div>
      `;
    } catch (error) {
      summaryContainer.innerHTML = `<strong>Ошибка:</strong> не удалось загрузить статистику`;
    }
  });

  loadMonthlyBtn.addEventListener('click', async () => {
    monthlyContainer.textContent = 'Загрузка месячного отчета...';

    try {
      const year = reportYear.value;
      const month = reportMonth.value;

      const response = await fetch(`/api/stats/monthly?year=${year}&month=${month}`);
      const data = await response.json();

      if (!data.success) {
        monthlyContainer.innerHTML = `<strong>Ошибка:</strong> ${data.message}`;
        return;
      }

      let salesTable = '';

      if (data.sales && data.sales.length > 0) {
        salesTable = `
          <table>
            <thead>
              <tr>
                <th>Товар</th>
                <th>Категория</th>
                <th>Количество</th>
                <th>Цена</th>
                <th>Сумма</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
        `;

        data.sales.forEach((sale) => {
          salesTable += `
            <tr>
              <td>${sale.productName}</td>
              <td>${sale.category}</td>
              <td>${sale.quantity}</td>
              <td>${sale.price}</td>
              <td>${sale.totalAmount}</td>
              <td>${new Date(sale.saleDate).toLocaleDateString()}</td>
            </tr>
          `;
        });

        salesTable += `
            </tbody>
          </table>
        `;
      } else {
        salesTable = `<p>За выбранный месяц продаж нет.</p>`;
      }

      monthlyContainer.innerHTML = `
        <div class="stat-item"><strong>Год:</strong> ${data.year}</div>
        <div class="stat-item"><strong>Месяц:</strong> ${data.month}</div>
        <div class="stat-item"><strong>Количество продаж:</strong> ${data.monthlySalesCount}</div>
        <div class="stat-item"><strong>Общая выручка за месяц:</strong> ${data.monthlyRevenue}</div>
        <div class="stat-item"><strong>Средний чек за месяц:</strong> ${data.monthlyAverageCheck.toFixed(2)}</div>
        ${salesTable}
      `;
    } catch (error) {
      monthlyContainer.innerHTML = `<strong>Ошибка:</strong> не удалось загрузить месячный отчет`;
    }
  });
});
