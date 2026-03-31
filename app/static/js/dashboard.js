/* =============================================================================
   dashboard.js
   Scripts for dashboard.html — ticket search & employee search
   ============================================================================= */

/* Ticket table search */
function filterTickets() {
  const q = document.getElementById('ticket-search').value.toLowerCase();
  document.querySelectorAll('#ticket-table tbody tr').forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

/* Employee / user list search */
function filterEmployees() {
  const input = document.getElementById('emp-search');
  if (!input) return;
  const q = input.value.toLowerCase();
  document.querySelectorAll('#emp-list .emp-row').forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}