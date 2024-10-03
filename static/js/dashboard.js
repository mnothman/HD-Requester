$(document).ready(function () {
    $('#partsTable').DataTable();  // Initialize DataTables on the table
});

// Function to update the dashboard table with new records
function updateDashboard(data) {
    const tableBody = document.querySelector('#partsTable tbody');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
    <td>${data.timestamp}</td>
    <td>${data.action}</td>
    <td>${data.TID}</td>
    <td>${data.unit_sn}</td>
    <td>${data.Type}</td>
    <td>${data.Capacity}</td>
    <td>${data.Size}</td>
    <td>${data.Speed}</td>
    <td>${data.Brand}</td>
    <td>${data.Model}</td>
    <td>${data.Part_sn}</td>
`;
    tableBody.appendChild(newRow);

    // Reinitialize DataTables to recognize the new row
    $('#partsTable').DataTable().row.add($(newRow)).draw();
}


function checkPartStatus(data) {
    fetch('/update_part_status', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDashboard(data.data);
            } else {
                console.error(data.message);
            }
        });
}