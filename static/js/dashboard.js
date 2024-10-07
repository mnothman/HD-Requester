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
    loadInventory();
    $('#partsTable').DataTable();  // Initialize DataTables on the table
    
});

/// Function to sanitize IDs for CSS selectors
function sanitizeId(id) {
    return id.replace(/[^a-zA-Z0-9-_]/g, '_'); // Replace invalid characters with underscores
}

// Function to fetch inventory data and dynamically create boxes
function loadInventory() {
    fetch('/get_inventory')
        .then(response => response.json())
        .then(data => {
            const container = $('.inventory-levels-container'); // Select the container where the boxes will be added
            container.empty(); // Clear existing content

            // Create a map to aggregate quantities by combined Type and Size
            const combinedMap = new Map();

            data.forEach(item => {
                const key = `${item.Type} ${item.Size}`;
                if (!combinedMap.has(key)) {
                    combinedMap.set(key, { quantity: item.quantity, capacities: [] });
                } else {
                    combinedMap.get(key).quantity += item.quantity;
                }
            });

            // Function to fetch capacities for a given Type and Size
            function fetchCapacities(type, size) {
                return fetch(`/get_part_capacities?type=${type}&size=${size}`)
                    .then(response => response.json())
                    .then(capacities => {
                        combinedMap.get(`${type} ${size}`).capacities = capacities;
                    });
            }

            // Function to create a box for each part type and its details
            function createBox(type, size, quantity, capacities, index) {
                const box = $('<div class="box"></div>'); // Create the box div

                // Create the box-header div with z-index and background color
                const boxHeader = $('<div class="box-header" style="z-index: 1;"></div>');
                const headerTitle = $('<h3></h3>').text(size === "null" ? `${type}` : `${type} ${size}`);

                // Set the background color based on cycling colors array
                boxHeader.css('background-color', colors[index % colors.length]);

                // Create a list of capacities to go below the h3 tag
                const capacitiesList = $('<ul class="capacities"></ul>');
                capacities.forEach(capacity => {
                    const li = $('<li></li>').text(capacity);
                    capacitiesList.append(li);
                });

                // Append the header title and capacities list to the box-header
                boxHeader.append(headerTitle);
                boxHeader.append(capacitiesList);

                // Create the box-data div for the quantity
                const boxData = $('<div class="box-data"></div>').text(`${quantity}`);

                // Append the box-header and box-data to the box
                box.append(boxHeader);
                box.append(boxData);

                // Set up click event to expand/collapse the box-header
                boxHeader.on('click', function () {
                    if (boxHeader.height() === 24) {
                        boxHeader.css('height', '170px').css('z-index', '2');
                        capacitiesList.toggleClass('show');
                    } else {
                        boxHeader.css('height', '24px');
                        capacitiesList.toggleClass('show');
                        boxHeader.on('transitionend', function () {
                            if (boxHeader.height() === 24) {
                                boxHeader.css('z-index', '1');
                            }
                        });
                    }
                });

                return box;
            }

            // Iterate over the part Types and Sizes, fetch capacities, and populate the boxes
            Promise.all(
                Array.from(combinedMap.keys()).map((key, index) => {
                    const [type, size] = key.split(' ');
                    return fetchCapacities(type, size).then(() => {
                        const { quantity, capacities } = combinedMap.get(key);
                        const box = createBox(type, size, quantity, capacities, index);
                        container.append(box); // Append each box to the container
                    });
                })
            ).catch(error => console.error('Error fetching capacities:', error));
        })
        .catch(error => console.error('Error fetching inventory data:', error));
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