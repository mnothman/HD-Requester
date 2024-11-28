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

    if (data.Type === "PC4" && data.Capacity.includes("GB")) {  // Check if it's RAM
        if (data.Size === "AiO") {
            data.Size = "Laptop";  // Set Size to Laptop for AiO RAM
            data.Technology = "AiO";  // Set Technology to AiO for RAM
        }
    }

    if (!data.Technology) {
        data.Technology = "--";
    }

    if (!data.Size) {
        data.Size = "--";
    }

// Technology is either: Desktop, Laptop, AiO, or Server. Size is laptop for RAM aio only, and -- for anything else.
    newRow.innerHTML = `
    <td>${data.timestamp}</td>
    <td>${data.action}</td>
    <td>${data.TID}</td>
    <td>${data.unit_sn}</td>
    <td>${data.Technology}</td> 
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
    const trendButtons = $('#trendButtons .btn');
    let trendsChart;

    // Initialize chart
    const ctx = document.getElementById('trendsChart').getContext('2d');

    // Function to initialize or update the chart
    function initChart(labels, datasets, title, chartType = 'line', xAxisLabel = 'Date') {
        if (trendsChart) {
            trendsChart.destroy();  
        }
        trendsChart = new Chart(ctx, {
            type: chartType,  // Use the passed chartType (default is 'line')
            data: {
                labels: labels,  // Dates or Unit SNs
                datasets: datasets  // Array of datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: { display: true, text: xAxisLabel }  // Dynamic x-axis title
                    },
                    y: {
                        title: { display: true, text: 'Transactions' },
                        beginAtZero: true
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            // Default callback behavior for tooltips
                            title: function(tooltipItems) {
                                const unitSN = tooltipItems[0].label;
                                return unitSN;
                            },
                            label: function(tooltipItem) {
                                return `${tooltipItem.raw} transactions`;
                            }
                        }
                    }
                }
            }
        });

        // Update chart title
        $('#parts-by-date-title').text(title);
    }

    // Handle month click
    monthsList.on('click', function () {
        monthsList.removeClass('active'); // Remove active class from all months
        $(this).addClass('active');  // Add active class to the clicked month
        
        // Remove active class from all trend buttons
        trendButtons.removeClass('active');

        const month = $(this).data('month');
        const year = new Date().getFullYear(); 
        
        // Fetch trends data
        $.getJSON(`/get_trends?month=${month}&year=${year}`, function (response) {
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

                // Line chart for trends
                initChart(dates, datasets, 'Parts by Date');
            } else {
                console.error('Error fetching trends:', response.message);
            }
        });
    });

    // Handle button click - make the clicked button active and store it
    trendButtons.on('click', function () {
        trendButtons.removeClass('active');  // Remove 'active' class from all buttons
        $(this).addClass('active');  // Add 'active' class to clicked button

        const buttonId = $(this).attr('id');
        const month = $('#monthsList .active').data('month');
        const year = new Date().getFullYear();

        // Fetch data based on the selected button
        if (buttonId === 'utilizationBtn') {
            $.getJSON(`/get_utilization?month=${month}&year=${year}`, function (response) {
                if (response.status === 'success') {
                    const utilization = response.data;
                    const dates = [month + '-' + year]; // Only one entry for month-year
                    const checkIns = [utilization.checked_in];
                    const checkOuts = [utilization.checked_out];

                    const datasets = [
                        {
                            label: 'Checked In',
                            data: checkIns,
                            backgroundColor: 'rgba(46, 204, 113, 0.2)',  // Green color for "Checked In"
                            borderColor: 'rgba(46, 204, 113, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Checked Out',
                            data: checkOuts,
                            backgroundColor: 'rgba(231, 76, 60, 0.2)',  // Red color for "Checked Out"
                            borderColor: 'rgba(231, 76, 60, 1)',
                            borderWidth: 1
                        }
                    ];

                    // Initialize the chart as a bar chart for Utilization
                    initChart(dates, datasets, 'Utilization', 'bar');
                }
            });
        } else if (buttonId === 'technologyBtn') {
            $.getJSON(`/get_technology?month=${month}&year=${year}`, function (response) {
                if (response.status === 'success') {
                    const technology = response.data;

                    // Extract the technology categories (keys) and their corresponding counts (values)
                    const techCategories = Object.keys(technology);  // Technology types: Apple, HD, etc.
                    const techCounts = Object.values(technology);    // Transaction counts for each type

                    const datasets = [{
                        label: 'Technology Transactions',
                        data: techCounts,
                        backgroundColor: 'rgba(52, 152, 219, 0.2)',  // Blue color for technology data
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    }];

                    // Initialize the chart as a bar chart, using technology categories for the x-axis
                    initChart(techCategories, datasets, 'Technology Transactions', 'bar', 'Technology Type');
                }
            });
        } else if (buttonId === 'upgradeBtn') {
            $.getJSON(`/get_upgrades?month=${month}&year=${year}`, function(response) {
                if (response.status === 'success') {
                    const data = response.data;
                    const days = Object.keys(data).sort();
                    const upgradeCounts = days.map(day => data[day]);
        
                    const ctx = document.getElementById('trendsChart').getContext('2d');
                    if (trendsChart) trendsChart.destroy();  // Destroy previous instance if exists
                    trendsChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: days,
                            datasets: [{
                                label: 'Daily Upgrades',
                                data: upgradeCounts,
                                backgroundColor: 'rgba(52, 152, 219, 0.5)',
                                borderColor: 'rgba(41, 128, 185, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Count of Upgrades'
                                    }
                                },
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Day of the Month'
                                    }
                                }
                            },
                            responsive: true,
                            plugins: {
                                legend: {
                                    display: true
                                }
                            }
                        }
                    });
                } else {
                    console.error('Failed to load data:', response.message);
                }
            });
          
        } else if (buttonId === 'repeatBtn') {
            $.getJSON(`/get_repeated?month=${month}&year=${year}`, function (response) {
                if (response.status === 'success') {
                    const repeated = response.data;

                    // Extract Unit SN, check count, status, and last request date
                    const unitSNs = repeated.map(item => item.Unit_sn);
                    const checkIns = repeated.filter(item => item.status === 'In').map(item => item.check_count);  // Filter check-ins
                    const checkOuts = repeated.filter(item => item.status === 'Out').map(item => item.check_count);  // Filter check-outs
                    const lastRequestDates = repeated.map(item => item.last_request_date);  // Last requested date

                    // Define datasets for check-ins and check-outs
                    const datasets = [
                        {
                            label: 'Repeated Check-ins',
                            data: checkIns,
                            backgroundColor: 'rgba(46, 204, 113, 0.2)',  // Green for check-ins
                            borderColor: 'rgba(46, 204, 113, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Repeated Check-outs',
                            data: checkOuts,
                            backgroundColor: 'rgba(231, 76, 60, 0.2)',  // Red for check-outs
                            borderColor: 'rgba(231, 76, 60, 1)',
                            borderWidth: 1
                        }
                    ];

                    // Initialize the chart as a stacked bar chart for Repeated Transactions
                    initChart(unitSNs, datasets, 'Repeated Transactions by Unit SN', 'bar', 'Unit SN');
                    
                    // Tooltip customization for repeated transactions
                    trendsChart.options.plugins.tooltip.callbacks = {
                        title: function(tooltipItems) {
                            const unitSN = tooltipItems[0].label;
                            const status = tooltipItems[0].datasetIndex === 0 ? 'Checked In' : 'Checked Out';
                            const date = lastRequestDates[unitSNs.indexOf(unitSN)]; // Get last request date for the current Unit SN
                            return `${status}: ${unitSN} | Last Request Date: ${date}`;
                        },
                        label: function(tooltipItem) {
                            return `Count: ${tooltipItem.raw}`;
                        }
                    };
                }
            });
        }
    });

    // Trigger click on first month to load initial data
    monthsList.first().trigger('click');
});

