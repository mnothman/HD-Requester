// Array of box headers
const boxHeaders = [
    'PC3 Desktop', 'PC3L Desktop', 'PC4 Desktop', 'SSD', 'HD 2.5"', 'Apple', 
    'PC3 Laptop', 'PC3L Laptop', 'PC4 Laptop', 'm.2', 'HD 3.5"', 'mSATA'
];

// Array of background colors to cycle through
const colors = [
    'rgb(202, 239, 69)', // Light Green
    'rgb(202, 239, 69)', // Light Green (repeated)
    'rgb(202, 160, 234)', // Light Purple
    'rgb(136, 211 ,223)', // Light Teal
    'rgb(209, 142, 163)', // Light Pink
    'rgb(194, 103, 103)', // Light Coral Red
    'rgb(153, 177, 68)', // Moss Green
    'rgb(153, 177, 68)', // Moss Green (repeated)
    'rgb(151, 110, 174)', // Dark Purple
    'rgb(70, 138, 149)', // Dark Teal
    'rgb(179, 99, 128)', // Dark Pink
    'rgb(152, 71, 79)'  // Dark Coral Red
];

$(document).ready(function () {
    populateBoxes();
    $('#partsTable').DataTable();  // Initialize DataTables on the table
});

// Function to populate the boxes dynamically with cycling colors
function populateBoxes() {
    // Select the container where the boxes will be added
    const container = $('.inventory-levels-container');
    
    // Clear the container before adding new boxes
    container.empty();

    // Iterate through the array of box headers
    boxHeaders.forEach((header, index) => {
        // Create the box div
        const box = $('<div class="box"></div>');

        // Create the box header div with inline background color
        const boxHeader = $('<div class="box-header"></div>');
        const headerTitle = $('<h3></h3>').text(header);

        // Set the background color of the header
        boxHeader.css('background-color', colors[index % colors.length]);
        
        // Append the header title to the header div
        boxHeader.append(headerTitle);

        // Create the box data div
        const boxData = $('<div class="box-data">NaN</div>');

        // Append the header and data divs to the box
        box.append(boxHeader);
        box.append(boxData);

        // Append the box to the container
        container.append(box);
    });
}



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