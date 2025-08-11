document.getElementById('receiptForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Collect form data and items
  const formData = new FormData(this);
  const items = [];
  document.querySelectorAll('#itemsTable tr').forEach(row => {
    const name = row.querySelector('[name="item_name"]')?.value;
    const qty = row.querySelector('[name="item_qty"]')?.value;
    const price = row.querySelector('[name="item_price"]')?.value;
    if (name && qty && price) {
      items.push({
        name: name,
        qty: parseInt(qty),
        price: parseFloat(price),
      });
    }
  });

  const receiptData = {
    customer: formData.get('customer'),
    items: items,
    tax: parseFloat(formData.get('tax')),
    discount: parseFloat(formData.get('discount')),
    payment: formData.get('payment'),
    total: parseFloat(document.getElementById('totalDisplay').value),
  };

  fetch('http://127.0.0.1:8000/receipt/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receiptData)
  })
    .then(res => res.json())
    .then(data => {
      console.log(data); // Debug: See what backend returns
      if (data && data.receipt_id) {
        showPreviewModal(data.receipt_id);
        showToast('Receipt generated successfully!');
      } else {
        showToast('Failed to generate receipt: Invalid response from server.');
      }
    })
    .catch(() => showToast('Failed to generate receipt.'));
});

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3000);
}

function addItemRow() {
  const table = document.getElementById('itemsTable');
  const row = document.createElement('tr');

  row.innerHTML = `
    <td class="px-4 py-2">
      <input type="text" class="w-full border px-2 py-1 rounded" name="item_name" required />
    </td>
    <td class="px-4 py-2">
      <input type="number" class="w-full border px-2 py-1 rounded" name="item_qty" min="1" value="1" required />
    </td>
    <td class="px-4 py-2">
      <input type="number" class="w-full border px-2 py-1 rounded" name="item_price" min="0" step="0.01" value="0.00" required />
    </td>
    <td class="px-4 py-2 text-center">
      <button type="button" onclick="removeItemRow(this)" class="text-red-600 hover:text-red-800">🗑️</button>
    </td>
  `;

  table.appendChild(row);
}

function removeItemRow(button) {
  button.closest('tr').remove();
}

function calculateTotal() {
  const rows = document.querySelectorAll('#itemsTable tr');
  let subtotal = 0;

  rows.forEach(row => {
    const qty = parseFloat(row.querySelector('[name="item_qty"]').value || 0);
    const price = parseFloat(row.querySelector('[name="item_price"]').value || 0);
    subtotal += qty * price;
  });

  const tax = parseFloat(document.querySelector('[name="tax"]').value || 0);
  const discount = parseFloat(document.querySelector('[name="discount"]').value || 0);

  const taxed = subtotal + (subtotal * tax / 100);
  const discounted = taxed - (taxed * discount / 100);

  document.getElementById('totalDisplay').value = discounted.toFixed(2);
}

// Recalculate on input change
document.addEventListener('input', function (e) {
  if (['item_qty', 'item_price', 'tax', 'discount'].includes(e.target.name)) {
    calculateTotal();
  }
});

// Only ONE event listener for form submission
document.getElementById('receiptForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Collect form data and items
  const formData = new FormData(this);
  const items = [];
  document.querySelectorAll('#itemsTable tr').forEach(row => {
    const name = row.querySelector('[name="item_name"]')?.value;
    const qty = row.querySelector('[name="item_qty"]')?.value;
    const price = row.querySelector('[name="item_price"]')?.value;
    if (name && qty && price) {
      items.push({
        name: name,
        qty: parseInt(qty),
        price: parseFloat(price),
      });
    }
  });

  const receiptData = {
    customer: formData.get('customer'),
    items: items,
    tax: parseFloat(formData.get('tax')),
    discount: parseFloat(formData.get('discount')),
    payment: formData.get('payment'),
    total: parseFloat(document.getElementById('totalDisplay').value),
  };

  fetch('http://127.0.0.1:8000/receipt/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receiptData)
  })
    .then(res => res.json())
    .then(data => {
      console.log(data); // Debug: See what backend returns
      if (data && data.receipt_id) {
        showPreviewModal(data.receipt_id);
        showToast('Receipt generated successfully!');
      } else {
        showToast('Failed to generate receipt: Invalid response from server.');
      }
    })
    .catch(() => showToast('Failed to generate receipt.'));
});

function showPreviewModal(receiptId) {
  const img = document.getElementById('receiptImage');
  img.src = `http://127.0.0.1:8000/receipt/render/${receiptId}`;
  const modal = document.getElementById('previewModal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function closeModal() {
  const modal = document.getElementById('previewModal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

function downloadReceipt() {
  const img = document.getElementById('receiptImage');
  const link = document.createElement('a');
  link.href = img.src;
  link.download = 'receipt.jpeg';
  link.click();
}

function emailReceipt() {
  // Placeholder: Replace with actual backend call
  showToast('📧 Receipt emailed successfully!');
}

function loadAllReceipts() {
  fetch('http://127.0.0.1:8000/receipt/all')
    .then(res => res.json())
    .then(receipts => {
      const tbody = document.getElementById('receiptsTable');
      tbody.innerHTML = '';
      receipts.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="px-4 py-2">${r.id}</td>
          <td class="px-4 py-2">${r.customer}</td>
          <td class="px-4 py-2">${r.total}</td>
          <td class="px-4 py-2">${r.payment}</td>
          <td class="px-4 py-2">${r.tax}</td>
          <td class="px-4 py-2">${r.discount}</td>
          <td class="px-4 py-2">
            <button onclick="showPreviewModal(${r.id})" class="text-blue-600 hover:underline">Preview</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    });
}

// Load receipts on page load
window.addEventListener('DOMContentLoaded', loadAllReceipts);
