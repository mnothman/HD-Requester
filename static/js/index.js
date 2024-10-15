$(document).ready(function () {
    $('#partsTable').DataTable({
        "ajax": {
            "url": "/get_parts",
            "type": "POST",
            "dataSrc": "data"
        },
        "columns": [
            { "data": "Type" },
            { "data": "Capacity" },
            { "data": "Size" },
            { "data": "Speed" },
            { "data": "Brand" },
            { "data": "Model" },
            { "data": "Location" },
            { "data": "Part_sn" }  // Serial number column
        ],
        "order": [[7, "dec"]]  // Sort by the Serial Number (Part_sn) column (index 7) in ascending order, "dec" is another option
    });
});


// Function to update the dashboard table with new records
function updateDashboard(data) {
    console.log(data)


    const tableBody = document.querySelector('#partsTable tbody');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
    <td>${data.Type}</td>
    <td>${data.Capacity}</td>
    <td>${data.Size}</td>
    <td>${data.Speed}</td>
    <td>${data.Brand}</td>
    <td>${data.Model}</td>
    <td>${data.Location}</td>
    <td>${data.Part_sn}</td>
`;
    tableBody.appendChild(newRow);

    

    // Reinitialize DataTables to recognize the new row
    $('#partsTable').DataTable().row.add($(newRow)).draw();
}


function checkPartStatus(data) {
    fetch('/get_parts', {
        method: 'GET',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDashboard(data.data);
                console.log(data.data)
            } else {
                console.error(data.message);
            }
        });
}

// split here

$(document).ready(function () {
    fetchAndDisplayParts();
    setupRowClick();

    /* ====== EVENT LISTENERS ===== */

    // Show/hide clear button functionality
    /*$('#searchInput').on('input', function () {
        var searchTerm = $(this).val().toLowerCase();

        // Show clear button if more than one character is entered
        if (searchTerm.length > 0) {
            $('#clearButton').show();
            $('#searchInput').addClass('inputFilled');
        } else {
            $('#clearButton').hide();
            $('#searchInput').removeClass('inputFilled');
        }


        // Need this to display all parts when search is deleted
        if (searchTerm === '') {
            fetchAndDisplayParts();  // Fetch and reset to show all parts
            return;
        }

        // Filter table rows based on the search term
        $('#partsTableBody tr').filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(searchTerm) > -1);
        });

        // Reapply classes to visible rows for alternating colors
        $('#partsTableBody tr').filter(":visible").each(function (index) {
            $(this).removeClass('odd-row even-row');  // Clear previous classes
            if (index % 2 === 0) {  // Even index, odd row (0-based index)
                $(this).addClass('odd-row');
            } else {  // Odd index, even row
                $(this).addClass('even-row');
            }
        });
    });

    // Clear input when clear button is clicked
    $('#clearButton').on('click', function () {
        $('#searchInput').val('');
        $(this).hide(); // Hide clear button after clearing the input

        // Show all rows after clearing the input
        $('#partsTableBody tr').show();

        // Reapply classes to visible rows for alternating colors
        $('#partsTableBody tr').each(function (index) {
            $(this).removeClass('odd-row even-row');
            if (index % 2 === 0) {
                $(this).addClass('odd-row');
            } else {
                $(this).addClass('even-row');
            }
        });
    });*/


    // Sort column
    $('.sortable-column').click(function () {
        var column = $(this).text().trim();  // Get the column name
        var sortOrder = $(this).attr('data-sort-order') || 'asc'; //get current sort order, default to ascending
        var searchTerm = $('#searchInput').val().toLowerCase();
        handleSort(column, sortOrder, searchTerm);

        sortOrder = (sortOrder === 'asc' ? 'desc' : 'asc');
        $(this).attr('data-sort-order', sortOrder);
    }); // end Sort column

    // IN/OUT Buttons
    document.querySelectorAll('.btn-group .btn').forEach(function (button) {
        button.addEventListener('click', function () {
            // Remove the active class from all buttons
            button.parentNode.querySelectorAll('.btn').forEach(function (btn) {
                btn.classList.remove('btn-active');
            });

            // Add the active class to the clicked button
            button.classList.add('btn-active');
        });
    }); // end in/out buttons

    $('.adminLogin').click(function () {
        $('#demo-buttons').toggle(); // This toggles the visibility
    });

    $('#btn-submit-request').click(function () {
        var parsedData = parseTextInput();
        var activeButton = document.querySelector('.btn-active');
        if (activeButton.innerText == "IN") {
            checkInPart(parsedData);
            // showLocationModal(parsedData);
        }
        else if (activeButton.innerText == "OUT") {
            checkOutPart(parsedData);
        }
        else {
            alert('Select IN or OUT')
            console.log(parsedData);
        }
    });

    $('#btnAddPart').click(function () {
        handleAddPart();
    });

    $('#rmvPartBtn').click(function () {
        var selectedParts = $('.selected-row');
        if (selectedParts.length > 0) {
            var partsList = selectedParts.map(function () {
                return $(this).children('td').map(function () {
                    return $(this).text().trim();
                }).get().join(', ');
            }).get().join('<br/>');

            var modalContent = '<p>Are you sure you want to remove the following parts?</p><p>' + partsList + '</p>';
            showModal({ title: 'Confirm Removal' }, modalContent, function () {
                removeSelectedParts(selectedParts);
            });
        } else {
            alert('No parts selected for removal.');
        }
    });

    // $('#rmvPartBtn').click(function () {
    // 	handleRemovePart();
    // });

    $('#btnDemoCheckin').click(function () {
        var demoPart = {
            "tid": "TI000000-00000001",
            "unit_sn": "123456",
            "parts": [{ "capacity": "1TB", "type": "SSD" }],
            "size": "Laptop",
            "serial_numbers": ["00000022"]
        }
        checkInPart(demoPart);
    });
    $('#btnDemoCheckinNotSeenBefore').click(function () {
        var demoPart = {
            "tid": "TI000000-00000001",
            "unit_sn": "123456",
            "parts": [{ "capacity": "99TB", "type": "SSD" }],
            "size": "Laptop",
            "serial_numbers": ["0000011"]
        }
        checkInPart(demoPart);
    });
    $('#btnDemoCheckinMismatch').click(function () {
        var demoPart = {
            "tid": "TI000000-00000001",
            "unit_sn": "123456",
            "parts": [{ "capacity": "8GB", "type": "PC4" }],
            "size": "Laptop",
            "serial_numbers": ["00000010"]
        }
        checkInPart(demoPart);
    });
    $('#btnDemoCheckout').click(function () {
        var demoPart = {
            "tid": "TI000000-00000001",
            "unit_sn": "123456",
            "parts": [{ "capacity": "2TB", "type": "HD" }],
            "size": "3.5",
            "serial_numbers": ["00000001"]
        }
        checkOutPart(demoPart);
    });
    $('#btnDemoCheckoutMismatch').click(function () {
        var demoPart = {
            "tid": "TI000000-00000001",
            "unit_sn": "123456",
            "parts": [{ "capacity": "1TB", "type": "HD" }],
            "size": "3.5",
            "serial_numbers": ["00000001"]
        }
        checkOutPart(demoPart);
    });
    $('#btnResetLogTables').click(function () {
        resetLogTables();
    });




    /* ====== FUNCTIONS ===== */
    function formatValue(value) {
        return value !== null && value !== undefined ? value : '-';
    }

    /*
    function fetchAndDisplayParts() {
        $.ajax({
            url: '/get_parts',
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                var tableBody = $('#partsTableBody');
                tableBody.empty(); // Clear existing rows
                $.each(data, function (index, part) {
                    var rowClass = (index % 2 === 0) ? 'odd-row' : 'even-row';
                    tableBody.append('<tr class="' + rowClass + '">' +
                        '<td>' + formatValue(part.Type) + '</td>' +
                        '<td>' + formatValue(part.Capacity) + '</td>' +
                        '<td>' + formatValue(part.Size) + '</td>' +
                        '<td>' + formatValue(part.Speed) + '</td>' +
                        '<td>' + formatValue(part.Brand) + '</td>' +
                        '<td>' + formatValue(part.Model) + '</td>' +
                        '<td>' + formatValue(part.Location) + '</td>' +
                        '<td>' + formatValue(part.Part_sn) + '</td>' +
                        '</tr>');
                });
            },
            error: function (xhr, status, error) {
                console.error("Error fetching parts data: " + error);
            }
        });
    }*/ // end fetchAndDisplayParts

    // Modal
    function showModal(dataObject, htmlContent, onConfirm) {
        // Set the content of the modal
        // Set the title of the modal if a title is provided in dataObject
        $('#modalContent').html(htmlContent);
        if (onConfirm) {
            $('#modalContent').append('<button id="confirmBtn" class="btn btn-success">Confirm</button>');
            $('#confirmBtn').click(function () {
                onConfirm();
                $('#Modal').css('display', 'none');
            });
        }

        if (dataObject && dataObject.title) {
            $('#modalTitle').text(dataObject.title);
        } else {
            // Default title if none provided
            $('#modalTitle').text('Details');
        }
        // Additional data handling could go here
        if (dataObject) {
            console.log("Additional data:", dataObject);
        }
        // Display the modal
        // Setup close button to hide the modal
        // Handle background clicks to also close the modal
        $('#Modal').css('display', 'block');
        $('#closeModalBtn').click(function () {
            $('#Modal').css('display', 'none');
        });
        $(window).click(function (event) {
            if ($(event.target).is('#Modal')) {
                $('#Modal').css('display', 'none');
            }
        });
    } // end Modal

    function handleSort(column, sortOrder) {
        var searchTerm = $('#searchInput').val().toLowerCase(); // Get the current search term to also allow for sorting

        // Make an AJAX request to the server to retrieve sorted data
        $.ajax({
            url: '/sort_parts',  // URL for sorting route in app.py
            method: 'POST',
            data: {
                column: column,
                order: sortOrder,
                search: searchTerm
            },
            success: function (response) {
                updateTable(response);
            },
            error: function (xhr, status, error) {
                console.error("Error sorting parts: " + error);
            }
        }); // end handleSort
    }

    function updateTable(parts) {
        var tableBody = $('#partsTableBody');
        tableBody.empty(); // Clear existing rows
        parts.forEach(function (part, index) {
            var rowClass = (index % 2 === 0) ? 'odd-row' : 'even-row';
            tableBody.append('<tr class="' + rowClass + '">' +
                `<td>${formatValue(part.Type)}</td>` +
                `<td>${formatValue(part.Capacity)}</td>` +
                `<td>${formatValue(part.Size)}</td>` +
                `<td>${formatValue(part.Speed)}</td>` +
                `<td>${formatValue(part.Brand)}</td>` +
                `<td>${formatValue(part.Model)}</td>` +
                `<td>${formatValue(part.Location)}</td>` +
                `<td>${formatValue(part.Part_sn)}</td>` +
                '</tr>');
        });
    }


    function handleAddPart() {
        const content = `
                    <p><strong>Add part manually</strong></p>

                    <form id="addPartForm">

                        <div class="form-group" style="display: flex; flex-direction: column; width: 100%; border: 1px solid #000;">
                            <!-- Header Row -->
                            <div class="form-row" style="display: flex; font-weight: bold; border-bottom: 1px solid #000; background-color: #f0f0f0;">
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Type</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Capacity</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Size</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Speed</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Brand</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Model</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Location</div>
                                <div class="form-col" style="flex: 1; padding: 8px; text-align: center;">Part SN</div>
                            </div>

                            <!-- Input Row -->
                            <div class="form-row" style="display: flex;">
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iType" name="Type" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iCapacity" name="Capacity" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <select id="ddSize" name="Size" style="width: 100%;">
                                        <option value="" selected> &nbsp; </option>
                                        <option value="Desktop">Desktop</option>
                                        <option value="Laptop">Laptop</option>
                                        <option value="2.5">2.5" HD</option>
                                        <option value="3.5">3.5" HD</option>
                                    </select>
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iSpeed" name="Speed" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iBrand" name="Brand" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iModel" name="Model" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iLocation" name="Location" style="width: 100%;" />
                                </div>
                                <div class="form-col" style="flex: 1; padding: 8px;">
                                    <input type="text" id="iPart_sn" name="Part SN" style="width: 100%;" />
                                </div>
                            </div>
                        </div>

                        <button type="button" id="add_btn" class="btn btn-primary mb-2">OK</button>
                    </form>



        `;
        showModal({ title: 'Add New Part' }, content);
        // Handle form submission
        $('#add_btn').click(function () {
            const partData = {
                Type: $('#iType').val(),
                Capacity: $('#iCapacity').val(),
                Size: $('#ddSize').val(),
                Speed: $('#iSpeed').val(),
                Brand: $('#iBrand').val(),
                Model: $('#iModel').val(),
                Location: $('#iLocation').val(),
                Part_sn: $('#iPart_sn').val()
            };
            submitPart(partData);
        });
    } // end handleAddPart

    //to click on rows to be removed using the remove button from handleRemovePart
    function setupRowClick() {
        $('#partsTableBody').on('click', 'tr', function () {
            $(this).toggleClass('selected-row');
            if ($(this).hasClass('selected-row')) {
                $(this).css('outline', '2px solid blue');
            } else {
                $(this).css('outline', 'none');
            }
        });
    }

    function removeSelectedParts(selectedRows) {
        var requests = selectedRows.map(function () {
            var partSn = $(this).find('td:last').text(); //part_sn is last in line. could be issue HERE
            var tid = 'System';
            var unit_sn = 'N/A';

            return $.ajax({
                url: '/update_part_status',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    Part_sn: partSn,
                    TID: tid,
                    Unit_sn: unit_sn,
                    Part_status: 'deleted'
                }),
                success: function (response) {
                    console.log('Success:', response);
                },
                error: function (xhr, status, error) {
                    console.error('Failed to mark part as deleted:', error);
                }
            });
        }).toArray();

        $.when.apply($, requests).then(function () {
            alert('All selected parts have been marked as deleted.');
            fetchAndDisplayParts();  // Refresh the parts list
        }, function () {
            alert('Failed to mark some or all parts as deleted.');
        });
    }



    // Function to submit part data to the server used by handleAddPart
    function submitPart(partData) {
        console.log(partData);

        $.ajax({
            url: '/add_part',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(partData),
            success: function (response) {
                if (response.status === 'success') {
                    alert('Part added successfully.');
                    $('#Modal').css('display', 'none'); // Close the modal
                    fetchAndDisplayParts();
                } else {
                    alert('Failed to add part: ' + response.message);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error adding part: ' + error);
                alert('Error adding part: ' + error);
            }
        });
    }
    function parseTextInput() {
        var textContent = document.getElementById('textarea-request').value;
        var noteContent = document.getElementById('textarea-notes').value;
        var lines = textContent.trim().split('\n');
        var dataObject = {
            tid: null,
            unit_sn: null,
            parts: [],
            size: null,
            serial_numbers: [],
            note: noteContent
        };

        if (lines.length < 4) { // Minimum number of lines for valid input
            console.error("Error: Insufficient input data.");
            return null;
        }

        // Parse TID
        dataObject.tid = lines[0].trim();
        if (!dataObject.tid.startsWith("TI") && !dataObject.tid.startsWith("TZZ")) {
            console.error("Error: Invalid TID format.");
            return null;
        }

        // Parse Unit_sn
        dataObject.unit_sn = lines[1].trim();
        if (!dataObject.unit_sn) {
            console.error("Error: Missing unit_sn.");
            return null;
        }

        // Parse parts and serial numbers
        var i = 2;
        while (lines[i] && !["Laptop", "Desktop", "Server"].includes(lines[i].trim())) {
            var details = lines[i].trim().split(' ');
            var part = {};

            if (details[0].match(/\d+(GB|TB)$/)) { // Drive
                part = {
                    capacity: details[0],
                    type: details.slice(1).join(' ')
                };
            } else { // RAM
                var capacityIndex = details.findIndex(detail => detail.match(/\d+(GB|MB)$/));
                part = {
                    type: details.slice(0, capacityIndex).join(' '),
                    capacity: details[capacityIndex]
                };
            }
            dataObject.parts.push(part);
            i++;
        }

        // Parse Size
        dataObject.size = lines[i].trim();
        i++;

        // Parse Serial Numbers
        while (i < lines.length) {
            dataObject.serial_numbers.push(lines[i].trim());
            i++;
        }

        if (dataObject.parts.length !== dataObject.serial_numbers.length) {
            console.error("Error: The number of parts does not match the number of serial numbers.");
            alert('Error: The number of parts does not match the number of serial numbers.');
            return null;
        }

        return dataObject;
    } // end parseTextInput

    function showLocationModal(partData) {
        const content = `
            <p><strong>Enter the location for the part:</strong></p>
            <form id="locationForm">
                <label for="locationInput">Location:</label>
                <input type="text" id="locationInput" name="location" style="width: 100%;" required>
                <button type="button" id="locationSubmitBtn" class="btn btn-primary mb-2">OK</button>
            </form>
        `;
        showModal({ title: 'Set Part Location' }, content);

        // Handle form submission
        $('#locationSubmitBtn').click(function () {
            const location = $('#locationInput').val();
            if (location) {
                partData.Location = location; // Set the location in part data
                checkInPart(partData); // Proceed to check in the part
                $('#Modal').css('display', 'none'); // Close modal
            } else {
                alert('Please enter a location');
            }
        });
    }

    function checkInPart(dataObject) {
        // Assume dataObject has already been parsed and structured
        dataObject.parts.forEach((part, index) => {
            const partSn = dataObject.serial_numbers[index];  // Get the serial number for the current part

            // Prepare the data to be sent to the server including Type and Capacity
            const partData = {
                Part_sn: partSn,
                Type: part.type,
                Capacity: part.capacity,
                Size: dataObject.size,
                Part_status: 'in',
                Note: dataObject.note
            };

            $.ajax({
                url: '/check_part_in_inventory',  // Server-side script to check the inventory
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(partData),
                success: function (response) {
                    if (response.exists) {
                        // If part exists and matches type and capacity, update its status to 'in'
                        const partSpeed = response.part?.Speed || 'N/A';  // Fallback to 'N/A' if undefined
                        const partBrand = response.part?.Brand || 'N/A';
                        const partModel = response.part?.Model || 'N/A';

                        const partDetails = `
                        <tr>
                            <td>${partData.Type}</td>
                            <td>${partData.Capacity}</td>
                            <td>${partData.Size}</td>
                            <td>${partBrand}</td>
                            <td>${partModel}</td>
                            <td><input type="text" id="locationInput" name="location" style="width: 100%;" placeholder="Enter location"></td>
                            <td>${partSn}</td>
                        </tr>
                    `;
                        const modalContent = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Capacity</th>
                                    <th>Size</th>
                                    <th>Brand</th>
                                    <th>Model</th>
                                    <th>Location</th>
                                    <th>Part SN</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${partDetails}
                            </tbody>
                        </table>
                        <button type="button" id="locationSubmitBtn" class="btn btn-primary mb-2">OK</button>
                    `;
                        showModal({ title: 'Enter Location for Check-in' }, modalContent);

                        // Handle form submission
                        $('#locationSubmitBtn').click(function () {
                            const location = $('#locationInput').val();
                            if (location) {
                                const partUpdateData = {
                                    Part_sn: partSn,
                                    TID: dataObject.tid,
                                    Unit_sn: dataObject.unit_sn,
                                    Part_status: 'in',
                                    Location: location,  // Add location from input
                                    Note: dataObject.note
                                };

                                console.log("Data being sent to /update_part_status: ", partUpdateData);
                                $('#locationSubmitBtn').prop('disabled', true);

                                $.ajax({
                                    url: '/update_part_status',
                                    type: 'POST',
                                    contentType: 'application/json',
                                    data: JSON.stringify(partUpdateData),
                                    success: function (updateResponse) {
                                        // fetchAndDisplayParts();
                                        console.log("Part checked in successfully", updateResponse);  // Log the response to ensure success


                                        if (updateResponse.status === 'success') {
                                            // Close the modal
                                            $('#Modal').css('display', 'none');

                                            fetchAndDisplayParts();


                                            // Trigger a page reload or fetch updated parts after a small delay
                                            setTimeout(function () {
                                                window.location.reload();  // Force page reload
                                                // location.reload #1
                                            }, 500);  // Delay to allow the modal to close smoothly
                                        } else {
                                            console.error("Failed to check in the part:", updateResponse.message);
                                            alert("Failed to check in the part: " + updateResponse.message);
                                        }
                                    },
                                    error: function (err) {
                                        console.error("Error updating part status: ", err);
                                        $('#locationSubmitBtn').prop('disabled', false);  // Re-enable button after failure
                                        alert('Failed to update part status: ' + err.responseText); // (Remove later)

                                    }
                                });
                                // $('#Modal').css('display', 'none'); // Close the modal
                            } else {
                                alert('Please enter a location');
                            }
                        });

                    } else {
                        // If part does not exist or does not match, show modal to add part
                        console.log(response.message); // Log the message from the server
                        // Check for specific mismatch error
                        if (response.error == 'mismatch') {
                            const expectedDetails = response.expected;
                            const actualDetails = response.actual;
                            const content = `
                                <p><strong>Expected: </strong>${expectedDetails.Capacity} ${expectedDetails.Type}</p>
                                <p><strong>Found: </strong>${actualDetails.Capacity} ${actualDetails.Type}</p>
                                
                            `;
                            showModal({ title: 'Check-in Error: ' + response.message }, content);
                        }
                        else if (response.error == 'checked-in') {
                            console.log("Error: " + response.message); // Handle other errors
                            const content = `
                            <!--
                                <p><strong>That part is already checked-in.<strong></p>
                                <p>Serial number: ${partSn}</p>
                                <table width="100%" border="1">
                                <tbody>
                                <tr>
                                  <th scope="col">&nbsp;Type</th>
                                  <th scope="col">Capacity&nbsp;</th>
                                  <th scope="col">Size&nbsp;</th>
                                  <th scope="col">Speed&nbsp;</th>
                                  <th scope="col">Brand&nbsp;</th>
                                  <th scope="col">Model&nbsp;</th>
                                  <th scope="col">Location&nbsp;</th>
                                </tr>
                                <tr>
                                    <td>${response.part['Type']}</td>
                                    <td>${response.part['Capacity']}</td>
                                    <td>${response.part['Size']}</td>
                                    <td>${response.part['Speed']}</td>
                                    <td>${response.part['Brand']}</td>
                                    <td>${response.part['Model']}</td>
                                    <td>${response.part['Location']}</td>
                                </tr>
                                </tbody>
                                </table>
                        -->
                                
                                    <p><strong>That part is already checked-in.</strong></p>
                                    <p>Serial number: ${partSn}</p>

                                    <div style="display: flex; flex-direction: column; width: 100%; border: 1px solid #000;">
                                        <div style="display: flex; font-weight: bold; border-bottom: 1px solid #000; background-color: #f0f0f0;">
                                            <div style="flex: 1; padding: 8px;">Type</div>
                                            <div style="flex: 1; padding: 8px;">Capacity</div>
                                            <div style="flex: 1; padding: 8px;">Size</div>
                                            <div style="flex: 1; padding: 8px;">Speed</div>
                                            <div style="flex: 1; padding: 8px;">Brand</div>
                                            <div style="flex: 1; padding: 8px;">Model</div>
                                            <div style="flex: 1; padding: 8px;">Location</div>
                                        </div>
                                        <div style="display: flex;">
                                            <div style="flex: 1; padding: 8px;">${response.part['Type']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Capacity']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Size']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Speed']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Brand']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Model']}</div>
                                            <div style="flex: 1; padding: 8px;">${response.part['Location']}</div>
                                        </div>
                                    </div>`
                                ;
                            showModal({ title: 'Check-in Error: ' + response.message }, content);

                        }
                        else if (response.error == 'not_in_inventory') {
                            console.log("Error: " + response.message); // Handle other errors

                            let speedField = ''; // Speed field isn't needed for HD or SSD

                            if (!["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type)) {  // Speed field isn't needed for HD or SSD
                                speedField = `
                                    <div style="flex: 1; padding: 8px;">Speed</div>
                                `;
                            }

                            const speedInput = !["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type) ? `
                                <div style="flex: 1; padding: 8px;">
                                    <input type="text" id="iSpeed" name="Speed" style="width: 100%;" />
                                </div>
                            ` : '';

                            // This below is for check in error when part is not in inventory
                            const content = `
                            <!--
                                <p><strong>That part has never been added to inventory.<strong></p>
                                <p>Serial number: ${partSn}</p>
                                <p>Add item to inventory. Fill in the blanks.</p>
                                <table width="100%" border="1">
                                <tbody>
                                <tr>
                                  <th scope="col">&nbsp;Type</th>
                                  <th scope="col">Capacity&nbsp;</th>
                                  <th scope="col">Size&nbsp;</th>
                                   ${speedField}
                                   <th scope="col">Brand&nbsp;</th>
                                  <th scope="col">Model&nbsp;</th>
                                  <th scope="col">Location&nbsp;</th>
                                </tr>
                                <tr>
                                    <td>${partData.Type}</td>
                                    <td>${partData.Capacity}</td>
                                    <td>${partData.Size}</td>
                                    <td><input type="text" id="iSpeed" name="Speed"></input></td>
                                    <td><input type="text" id="iBrand" name="Brand"></input></td>
                                    <td><input type="text" id="iModel" name="Model"></input></td>
                                    <td><input type="text" id="iLocation" name="Location"></input></td>
                                </tr>
                                </tbody>
                                </table>-->

                                <p><strong>That part has never been added to inventory.</strong></p>
                                    <p>Serial number: ${partSn}</p>
                                    <p>Add item to inventory. Fill in the blanks.</p>

                                    <div style="display: flex; flex-direction: column; width: 100%; border: 1px solid #000;">
                                        <!-- Header Row -->
                                        <div style="display: flex; font-weight: bold; border-bottom: 1px solid #000; background-color: #f0f0f0;">
                                            <div style="flex: 1; padding: 8px;">Type</div>
                                            <div style="flex: 1; padding: 8px;">Capacity</div>
                                            <div style="flex: 1; padding: 8px;">Size</div>
                                               ${speedField}
                                            <div style="flex: 1; padding: 8px;">Brand</div>
                                            <div style="flex: 1; padding: 8px;">Model</div>
                                            <div style="flex: 1; padding: 8px;">Location</div>
                                            <div style="flex: 1; padding: 8px;">Part SN</div>
                                        </div>
                                        
                                        <!-- Data Row -->
                                        <div style="display: flex;">

                                            <!--
                                                <div style="flex: 1; padding: 8px;" id="iType">${partData.Type}</div>
                                                <div style="flex: 1; padding: 8px;">${partData.Capacity}</div>
                                                <div style="flex: 1; padding: 8px;">${partData.Size}</div>
                                            -->

                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iType" name="Type" style="width: 100%;" value="${partData.Type}"/>
                                            </div>

                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iCapacity" name="Type" style="width: 100%;" value="${partData.Capacity}"/>
                                            </div>

                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="ddSize" name="Type" style="width: 100%;" value="${partData.Size}"/>
                                            </div>
                                            ${speedInput}
                                            
                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iBrand" name="Brand" style="width: 100%;" />
                                            </div>
                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iModel" name="Model" style="width: 100%;" />
                                            </div>
                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iLocation" name="Location" style="width: 100%;" />
                                            </div>

                                            <div style="flex: 1; padding: 8px;">
                                                <input type="text" id="iPart_sn" name="Part SN" style="width: 100%;" value="${partSn}"/>
                                            </div>

                                            
                                        </div>

                                        
                                    </div>

                                    <div style="margin-top: 10px;">
                                        <button type="button" id="add_btn" class="btn btn-primary mb-2">Add Part</button>	
                                    </div>

                                    

                            `;
                            showModal({ title: 'Check-in Error: ' + response.message }, content);

                            // Handle form submission - Add The Part
                            $('#add_btn').click(function () {
                                const partData = {
                                    Type: $('#iType').val(),
                                    Capacity: $('#iCapacity').val(),
                                    Size: $('#ddSize').val(),
                                    Speed: $('#iSpeed').val(),
                                    Brand: $('#iBrand').val(),
                                    Model: $('#iModel').val(),
                                    Location: $('#iLocation').val(),
                                    Part_sn: $('#iPart_sn').val()
                                };

                                console.log(partData);
                                submitPart(partData);
                            });
                        }
                    }
                },
                error: function (err) {
                    console.error("Error checking part in inventory: ", err);
                    alert('Error checking part in inventory: ' + error);
                }
            });
        });
    } // end checkinPart

    function checkOutPart(dataObject) {
        // Assume dataObject has already been parsed and structured
        dataObject.parts.forEach((part, index) => {
            const partSn = dataObject.serial_numbers[index];  // Get the serial number for the current part

            // Prepare the data to be sent to the server including Type and Capacity
            const partData = {
                Part_sn: partSn,
                Type: part.type,
                Capacity: part.capacity,
                Size: dataObject.size,
                Speed: dataObject.Speed,
                Part_status: 'out',
                Note: dataObject.note
            };

            $.ajax({
                url: '/check_part_in_inventory',  // Server-side script to check the inventory
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(partData),
                success: function (response) {
                    if (response.exists) {
                        // If part exists and matches type and capacity, update its status to 'out'
                        $.ajax({
                            url: '/update_part_status',
                            type: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                Part_sn: partSn,
                                TID: dataObject.tid,
                                Unit_sn: dataObject.unit_sn,
                                Part_status: 'out',
                                Note: dataObject.note
                            }),
                            success: function (updateResponse) {
                                fetchAndDisplayParts();

                                // refreshes page after checking out
                                location.reload();
                                print("location reload 2");
                                // location.reload #2
                            },
                            error: function (err) {
                                console.error("Error updating part status: ", err);
                            }
                        });
                    } else {
                        // If part does not exist or does not match, show modal to add part
                        console.log(response.message); // Log the message from the server
                        // Check for specific mismatch error
                        if (response.error == 'mismatch') {
                            const expectedDetails = response.expected;
                            const actualDetails = response.actual;
                            const content = `
                                <p><strong>Expected: </strong>${expectedDetails.Capacity} ${expectedDetails.Type}</p>
                                <p><strong>Found: </strong>${actualDetails.Capacity} ${actualDetails.Type}</p>
                                
                            `;
                            showModal({ title: 'Check-out Error: ' + response.message }, content);
                        }
                        else if (response.error == 'checked-out') {
                            console.log("Error: " + response.message); // Handle other errors
                            const content = `
                                <p><strong>That part is already checked-out.<strong></p>
                                <p>Serial number: ${partSn}</p>
                                <table width="100%" border="1">
                                <tbody>
                                <tr>
                                  <th scope="col">&nbsp;Type</th>
                                  <th scope="col">Capacity&nbsp;</th>
                                  <th scope="col">Size&nbsp;</th>
                                  <th scope="col">Speed&nbsp;</th>
                                  <th scope="col">Brand&nbsp;</th>
                                  <th scope="col">Model&nbsp;</th>
                                  <th scope="col">Location&nbsp;</th>
                                </tr>
                                <tr>
                                    <td>${response.part['Type']}</td>
                                    <td>${response.part['Capacity']}</td>
                                    <td>${response.part['Size']}</td>
                                    <td>${response.part['Speed']}</td>
                                    <td>${response.part['Brand']}</td>
                                    <td>${response.part['Model']}</td>
                                    <td>${response.part['Location']}</td>
                                </tr>
                                </tbody>
                                </table>
                            `;
                            showModal({ title: 'Check-out Error: ' + response.message }, content);
                        }
                        // This is if the part does not exist in database and needs to be added manually
                        else if (response.error == 'not_in_inventory') {
                            console.log("Error: " + response.message); // Handle other errors

                            const content = `
                                <p><strong>That part has never been added to inventory.</strong></p>
                                <p>Serial number: ${partSn}</p>
                                <p>Add item to inventory. Fill in the blanks.</p>
                                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
                                <thead>
                                    <tr style="background-color: #f0f0f0; text-align: left; font-weight: bold;">
                                        <th style="padding: 8px; width: 10%;">Type</th>
                                        <th style="padding: 8px; width: 10%;">Capacity</th>
                                        <th style="padding: 8px; width: 10%;">Size</th>
                                        <th style="padding: 8px; width: 10%;">Speed</th>
                                        <th style="padding: 8px; width: 10%;">Brand</th>
                                        <th style="padding: 8px; width: 10%;">Model</th>
                                        <th style="padding: 8px; width: 15%;">Location</th>
                                    </tr>
                                <tr>
                                    <td style="padding: 8px;">${partData.Type}</td>
                                    <td style="padding: 8px;">${partData.Capacity}</td>
                                    <td style="padding: 8px;">${partData.Size}</td>
                                    <td style="padding: 8px;"><input type="text" id="iSpeed" name="Speed" style="width: 100%;"></td>
                                    <td style="padding: 8px;"><input type="text" id="iBrand" name="Brand" style="width: 100%;"></td>
                                    <td style="padding: 8px;"><input type="text" id="iModel" name="Model" style="width: 100%;"></td>
                                    <td style="padding: 8px;"><input type="text" id="iLocation" name="Location" style="width: 100%;">
                                </td>
                                </tr>
                                </tbody>
                                </table>

                                <div style="margin-top: 10px;">
                                    <button type="button" id="add_btn" class="btn btn-primary mb-2">Add Part</button>
                                </div>
                            `;

                            showModal({ title: 'Check-out Error: ' + response.message }, content);

                            const originalPartData = partData;  // Store the original partData outside the click handler


                            // Handle form submission when the user clicks "Add Part"
                            $('#add_btn').click(function () {
                                const newPartData = {
                                    Type: originalPartData.Type, // Use the original Type
                                    Capacity: $('#iCapacity').val(),
                                    Size: $('#ddSize').val(),
                                    Speed: $('#iSpeed').val(),
                                    Brand: $('#iBrand').val(),
                                    Model: $('#iModel').val(),
                                    Location: $('#iLocation').val(),
                                    Part_sn: partSn  // Use the original part serial number
                                };

                                console.log('Part data being sent:', newPartData);

                                // Submit the part to the server
                                submitPart(newPartData);
                            });
                        }
                    }
                },
                error: function (err) {
                    console.error("Error checking part out inventory: ", err);
                    alert('Error checking part out inventory: ' + err);
                }
            });
        });
    } // end checkoutPart

    function resetLogTables() {
        $.ajax({
            url: '/reset_log_tables',  // URL of the Flask endpoint
            type: 'POST',  // Method type, as defined in your Flask route
            contentType: 'application/json',  // Data type expected to send (if you are sending data to the server)
            success: function (response) {
                // This function is called if the request succeeds.
                console.log('Response:', response);
                alert('Database has been reset successfully.');
                fetchAndDisplayParts();
            },
            error: function (xhr, status, error) {
                // This function is called if the request fails.
                console.error('Error resetting database:', error);
                alert('Failed to reset database: ' + error);
            }
        });
    } // end resetLogTables

});

//Code to display a text areas for adding a note to a part
document.addEventListener("DOMContentLoaded", function () {
    const toggleNotesBtn = document.getElementById("toggleNotesBtn");
    const notesContainer = document.getElementById("notesContainer");
    const textarea = document.getElementById("textarea-notes"); // Get the textarea

    // Ensure notes container is hidden initially
    notesContainer.style.display = "none";

    toggleNotesBtn.onclick = function () {
        if (notesContainer.style.display === "none") {
            notesContainer.style.display = "block";
        } else {
            notesContainer.style.display = "none";
            textarea.value = ""; // Clear the textarea when hiding
        }
    };
});