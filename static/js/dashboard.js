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

    //new DataTable('#partsTable', {
    //    order: [0, 'dec']
    //});
    //Removed extra DataTable setup to avoid repeating and make sure the partsTable works properly. 

    const partsTable = new DataTable('#partsTable', {
        order: [0, 'dec']
    });

    // Setup to add ID for the live search bar
    $('#partsTable_filter input').attr('id', 'searchInput');
    // Setup clear button to search bar
    $('#partsTable_filter').append('<button id="clearButton">&times;</button>');

    // Show/hide clear button functionality
    $('#searchInput').on('input', function () {
        var searchTerm = $(this).val().toLowerCase();

        // Show clear button if more than one character is entered
        if (searchTerm.length > 0) {
            $('#clearButton').show();
            $('#searchInput').addClass('inputFilled');
        } else {
            $('#clearButton').hide();
            $('#searchInput').removeClass('inputFilled');
        }
    });

    // Clear search bar when clear icon is clicked
    $('#clearButton').on('click', function () {
        $('#searchInput').val('');
        partsTable.search('').draw();
        $(this).hide(); // Hide clear button after clearing the input
    });    
    
    // Sidebar toggle functionality
    const hamburgerBtn = $('#hamburgerBtn');
    const sidebar = $('#sidebar');
    hamburgerBtn.on('click', function() {
        sidebar.toggleClass('active');
    }); 
});

/// Function to sanitize IDs for CSS selectors
function sanitizeId(id) {
    return id.replace(/[^a-zA-Z0-9-_]/g, '_'); // Replace invalid characters with underscores
}

// Function to fetch part counts for the selected capacity and size
async function fetchPartCount(type, capacity, size) {
    try {
        const response = await fetch(`/get_part_count?type=${type}&capacity=${capacity}&size=${size}`);
        const data = await response.json();

        if (data.count !== undefined) {
            return data.count;  // Return the count
        } else {
            console.error('No count returned from API');
            return 0;  // Return 0 if there's an issue
        }
    } catch (error) {
        console.error('Error fetching part count:', error);
        return 0;  // Return 0 if there's an error
    }
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
            async function fetchCapacities(type, size) {
                try {
                    const response = await fetch(`/get_part_capacities?type=${type}&size=${size}`);
                    const capacities = await response.json();
                    combinedMap.get(`${type} ${size}`).capacities = capacities;
                } catch (error) {
                    console.error('Error fetching capacities:', error);
                }
            }
            
            // Function to create a box for each part type and its details
            function createBox(type, size, quantity, capacities, index) {
                const box = $('<div class="box"></div>'); // Create the box div

                // Create the box-header div with z-index and background color
                const boxHeader = $('<div class="box-header" style="z-index: 1;"></div>');

                // Store original header title for future reference
                const originalHeaderTitle = size === "null" ? `${type}` : `${type} ${size}`;
                const headerTitle = $('<h3></h3>').text(originalHeaderTitle);

                // Store original count for reset later
                const originalCount = quantity; // Local variable to store the original count for Type and Size

                // Set the background color based on cycling colors array
                boxHeader.css('background-color', colors[index % colors.length]);

                // Create a list of capacities to go below the h3 tag
                const capacitiesList = $('<ul class="capacities"></ul>');
                capacities.forEach(capacity => {
                    const li = $('<li></li>').text(capacity);
                    capacitiesList.append(li);

                    // Add click handler to fetch count of parts for the selected capacity
                    li.on('click', function () {
                        fetchPartCount(type, capacity, size).then(count => {
                            boxData.text(`${count}`); // Update the quantity displayed
                            // Prepend the selected capacity to the original part type in the h3
                            headerTitle.text(`${capacity} ${originalHeaderTitle}`);
                            boxHeader.toggleClass('show'); // Hide the dropdown after selection
                        });
                    });
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
                        boxHeader.css('height', 'auto').css('z-index', '2');
                        capacitiesList.toggleClass('show');
                    } else {
                        boxHeader.css('height', '24px').css('z-index', '1');
                        capacitiesList.toggleClass('show');

                        // Reset the headerTitle to the originalHeaderTitle
                        headerTitle.text(originalHeaderTitle);

                        // Reset the boxData back to the original count when closing
                        boxData.text(`${originalCount}`); // Reset to original Type and Size count

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

                    // Fetch the count for each capacity and update the box text
                    capacities.forEach(capacity => {
                        fetchPartCount(type, capacity).then(count => {
                            const sanitizedId = sanitizeId(`${type}_${size}_${capacity}`);
                            const boxData = document.getElementById(sanitizedId);
                            if (boxData) {
                                boxData.textContent = `Count: ${count}`;
                            }
                        });
                    });
                });
            })
        ).catch(error => console.error('Error fetching capacities:', error));
    })
    .catch(error => console.error('Error fetching inventory data:', error));
}

// Function to update the dashboard table with new records
function updateDashboard(data) {
    console.log(data)


    const tableBody = document.querySelector('#partsTable tbody');
    const newRow = document.createElement('tr');

    if (data.Technology === "AiO" && data.Capacity === "RAM") {
        data.Size = "Laptop";  
    } else {
        if (data.Size === "AiO") {
            data.Technology = "AiO";
            data.Size = "";
        }
    }

    if (!data.Technology) {
        data.Technology = "--";
    }

    if (!data.Size) {
        data.Size = "--";
    }


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
    <td>${data.Note}</td>
`;
    tableBody.appendChild(newRow);


    // Reinitialize DataTables to recognize the new row
    $('#partsTable').DataTable().row.add($(newRow)).draw();

    console.log('updateDashbaord')
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

$(document).ready(function () {
    const monthsList = $('#monthsList li');
    let trendsChart;

    // Initialize chart
    const ctx = document.getElementById('trendsChart').getContext('2d');
    function initChart(labels, datasets) {
        if (trendsChart) {
            trendsChart.destroy();  
        }
        trendsChart = new Chart(ctx, {
            type: 'line',  
            data: {
                labels: labels,  // Dates
                datasets: datasets  // Array of datasets: check-ins, check-outs)
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: { display: true, text: 'Date' }
                    },
                    y: {
                        title: { display: true, text: 'Transactions' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Handle month click
    monthsList.on('click', function () {
        monthsList.removeClass('active'); // Remove active class from all months
        $(this).addClass('active');  // Add active class to the clicked month
        
        const month = $(this).data('month');
        const year = new Date().getFullYear(); 
        
        // Fetch trends data
        $.getJSON(`/get_trends?month=${month}&year=${year}`, function (response) {
            console.log(response);  
            if (response.status === 'success') {
                const trends = response.data;
                
                const dates = Object.keys(trends);
                const checkIns = dates.map(date => trends[date].check_ins);
                const checkOuts = dates.map(date => trends[date].check_outs);
                const laptops = dates.map(date => trends[date].laptop_transactions);
                const desktops = dates.map(date => trends[date].desktop_transactions);

                const datasets = [
                    {
                        label: 'Check-ins',
                        data: checkIns,
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Check-outs',
                        data: checkOuts,
                        backgroundColor: 'rgba(231, 76, 60, 0.2)',
                        borderColor: 'rgba(231, 76, 60, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Laptop',
                        data: laptops,
                        backgroundColor: 'rgba(52, 152, 219, 0.2)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Desktop',
                        data: desktops,
                        backgroundColor: 'rgba(241, 196, 15, 0.2)',
                        borderColor: 'rgba(241, 196, 15, 1)',
                        borderWidth: 1
                    }
                ];
                
                initChart(dates, datasets);
            } else {
                console.error('Error fetching trends:', response.message);
            }
        });
    });

    monthsList.first().trigger('click');
});
