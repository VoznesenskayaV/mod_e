document.addEventListener('DOMContentLoaded', () => {

  const checkServerBtn = document.getElementById('checkServerBtn');
  const serverStatus = document.getElementById('serverStatus');

  const checkDbBtn = document.getElementById('checkDbBtn');
  const dbStatus = document.getElementById('dbStatus');

  const loadSalesBtn = document.getElementById('loadSalesBtn');
  const salesContainer = document.getElementById('salesContainer');

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

});
