// Global variable
var partsTable = $('#partsTable').DataTable({
    autoFill: true,
    responsive: true,
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
    "order": [[7, "asc"]],  // Sort by the Serial Number (Part_sn) column (index 7) in ascending order, "dec" is another option
    "columnDefs": [{
        "targets": '_all',
        "defaultContent": "—"
    }],
});

$(document).ready(function () {
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

    //Code to display a text areas for adding a note to a part
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

    setupRowClick();

    /* ====== EVENT LISTENERS ===== */

    /*  deleted Sortable column on 10-17/2024
        because we implemented a new way to sort
        the table columns. RC
    */

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

    $('#btn-submit-request').click(function () {
        var parsedData = parseTextInput();
        var activeButton = document.querySelector('.btn-active');
        if (activeButton.innerText == "IN") {
            checkInPart(parsedData);
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

    // Handle right-click on table row
    $('#partsTable tbody').on('contextmenu', 'tr', function (e) {
        e.preventDefault();  // Prevent the default right-click context menu

        // Get the part data from the row
        const partData = $(this).children("td").map(function () {
        return $(this).text();
        }).get();

        // Show context menu at mouse position
        $(".context-menu").css({
        display: "block",
        left: e.pageX + "px",
        top: e.pageY + "px"
        }).data('partData', partData); // Attach part data to the context menu
    });

    // Hide context menu when clicking elsewhere
    $(document).on("click", function () {
        $(".context-menu").hide();
    });

    // Handle clicking "Edit" in the context menu
    $(".context-menu .edit").on("click", function () {
        const partData = $(".context-menu").data('partData');

         // Populate the modal form with the part data
        $("#editType").val(partData[0]);
        $("#editCapacity").val(partData[1]);
        $("#editSize").val(partData[2]);
        $("#editSpeed").val(partData[3]);
        $("#editBrand").val(partData[4]);
        $("#editModel").val(partData[5]);
        $("#editLocation").val(partData[6]);
        $("#editPart_sn").val(partData[7]);

        // Show the modal
        $("#editPartModal").show();

        // Hide the context menu
        $(".context-menu").hide();
    });

    // Close the modal when clicking close button
    $('#closeModalBtn').click(function () {
        $('#editPartModal').hide();
    });

    // Handle form submission for editing a part
    $('#editPartForm').submit(function (e) {
        e.preventDefault();

        const updatedPartData = {
        type: $('#editType').val(),
        capacity: $('#editCapacity').val(),
        size: $('#editSize').val(),
        speed: $('#editSpeed').val(),
        brand: $('#editBrand').val(),
        model: $('#editModel').val(),
        location: $('#editLocation').val(),
        part_sn: $('#editPart_sn').val()
        };

        // AJAX call to update the part in the database
        $.ajax({
            url: '/update_part',
            type: 'POST',
            data: JSON.stringify(updatedPartData),
            contentType: 'application/json',
            success: function (response) {
                partsTable.ajax.reload(null, false);
                alert("Part updated successfully.");
            },
        error: function (xhr, status, error) {
            alert("Error updating part: " + error);
        }
        });

        // Close the modal after submission
        $('#editPartModal').hide();
    });
});

/* ====== FUNCTIONS ===== */
/*  deleted formatValue() on 10-17-2024
    because we are replacing null values as the
    table is rendered. RC
*/

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

/*  deleted updateDashboard(data) on 10-17-2024
    because it was an exact copy. RC
*/

/*  deleted fetchAndDisplayParts() on 10/17/2024
    because we're using a new way to get the parts
    and display them. RC
*/

/*  deleted copy of checkPartStatus(data) on 10-17-2024
    because it was an exact copy. RC
*/

function updateDashboard(data) {
    const tableBody = document.querySelector('#partsTable tbody');
    tableBody.appendChild(newRow);

    // Reinitialize DataTables to recognize the new row
    partsTable.DataTable().row.add($(newRow)).draw();
}

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
    // close modal
    $('#closeModalBtn').click(function () {
        $('#Modal').css('display', 'none');
    });
    $(window).click(function (event) {
        if ($(event.target).is('#Modal')) {
            $('#Modal').css('display', 'none');
        }
    });
} // end Modal

    /*  deleted handleSort on 10-17-2024
        because we implemented sorting differently
        RC
    */
    /*  deleted updateTable(parts) on 10-17-2024
        because we are displaying the new row as it's
        created. RC
    */

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
        $('#partsTable tbody').on('click', 'tr', function () {
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
            var tid = 'System';     // the endpoint update_part_status needs these variables, but removePart doesn't have it
            var unit_sn = 'N/A';
            var note = "Deleted from homepage";

            return $.ajax({
                url: '/update_part_status',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    Part_sn: partSn,
                    TID: tid,
                    Unit_sn: unit_sn,
                    Part_status: 'Deleted',
                    Note: note
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
            partsTable.ajax.reload(null, false);
        }, function () {
            alert('Failed to mark some or all parts as deleted.');
        });
    }


/*  deleted updateDataTable on 10-17-2024
    because it isn't being used. RC
*/

    // Function to submit part data to the server used by handleAddPart
    function submitPart(partData) {
        $.ajax({
            url: '/add_part',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(partData),
            success: function (response) {
                if (response.status === 'success') {
                    partsTable.ajax.reload(null, false);
                    alert('Part added successfully.');
                    $('#Modal').css('display', 'none'); // Close the modal
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
        if (!dataObject.tid.startsWith("TI") &&
            !dataObject.tid.startsWith("TT") &&
            !dataObject.tid.startsWith("TZZ")) {
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
        dataObject.parts.forEach((part, index) => {
            const partSn = dataObject.serial_numbers[index];  // Get the serial number for the current part
            const unitSn = dataObject.unit_sn;  // Get the Unit Serial Number
    
            // Validate if Unit Serial Number is missing
            if (!unitSn) {
                const content = `
                    <p><strong>Unit Serial Number is missing.</strong></p>
                    <p>Please provide a valid serial number for part: ${partSn}.</p>
                `;
                showModal({ title: 'Error: Missing Unit Serial Number' }, content);
                return;  // Prevent further execution for this part
            }
    
            // Prepare the data to be sent to the server including Type and Capacity
            const partData = {
                Part_sn: partSn,
                Type: part.type,
                Capacity: part.capacity,
                Size: dataObject.size,
                Part_status: 'In',
                Unit_sn: unitSn,  // Include the valid Unit Serial Number here
                Note: dataObject.note
            };
    
            $.ajax({
                url: '/check_part_in_inventory',  // Server-side script to check the inventory
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(partData),
                success: function (response) {
                    if (response.exists) {
                        // If part exists and matches type and capacity, update its status to 'In'
                        const partSpeed = response.part?.Speed || 'N/A';
                        const partBrand = response.part?.Brand || 'N/A';
                        const partModel = response.part?.Model || 'N/A';
    
                        const partDetails = `
                            <div style="display: flex;">
                                <div style="flex: 1; padding: 8px;">${partData.Type}</div>
                                <div style="flex: 1; padding: 8px;">${partData.Capacity}</div>
                                <div style="flex: 1; padding: 8px;">${partData.Size}</div>
                                <div style="flex: 1; padding: 8px;">${partBrand}</div>
                                <div style="flex: 1; padding: 8px;">${partModel}</div>
                                <div style="flex: 1; padding: 8px;"><input type="text" id="locationInput" name="location" style="width: 100%;" placeholder="Enter location"></div>
                                <div style="flex: 1; padding: 8px;">${partSn}</div>
                            </div>
                        `;
                        const modalContent = `
                            <div class="modal-table-wrapper">
                                <div class="modal-table-header">
                                    <div style="flex: 1; padding: 8px;">Type</div>
                                    <div style="flex: 1; padding: 8px;">Capacity</div>
                                    <div style="flex: 1; padding: 8px;">Size</div>
                                    <div style="flex: 1; padding: 8px;">Brand</div>
                                    <div style="flex: 1; padding: 8px;">Model</div>
                                    <div style="flex: 1; padding: 8px;">Location</div>
                                    <div style="flex: 1; padding: 8px;">Part SN</div>
                                </div>
                                ${partDetails}
                            </div>
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
                                    Unit_sn: unitSn,  // Include Unit Serial Number here
                                    Part_status: 'In',
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
                                        if (updateResponse.status === 'success') {
                                            partsTable.ajax.reload(null, false);
                                            $('#Modal').css('display', 'none'); // Close modal
                                        } else {
                                            console.error("Failed to check in the part:", updateResponse.message);
                                            alert("Failed to check in the part: " + updateResponse.message);
                                        }
                                    },
                                    error: function (err) {
                                        console.error("Error updating part status: ", err);
                                        $('#locationSubmitBtn').prop('disabled', false);
                                        alert('Failed to update part status: ' + err.responseText);
                                    }
                                });
                            } else {
                                alert('Please enter a location');
                            }
                        });
    
                    } else {
                        // If part does not exist or does not match, show modal with error message
                        handleCheckInErrors(response, partSn);
                    }
                },
                error: function (err) {
                    console.error("Error checking part in inventory: ", err);
                    alert('Error checking part in inventory: ' + err.responseText);
                }
            });
        });
    }
    
    // Function to handle edge case errors during check-in
    function handleCheckInErrors(response, partSn) {
        if (response.error === 'size_mismatch') {
            const content = `
                <p><strong>Size mismatch detected:</strong></p>
                <p>Expected: ${response.expected.Size}</p>
                <p>Provided: ${response.actual.Size}</p>
                <p>Please correct the Size.</p>
            `;
            showModal({ title: 'Check-in Error: Size Mismatch' }, content);
        } else if (response.error === 'mismatch') {
            const content = `
                <p><strong>Mismatch detected:</strong></p>
                <p>Expected: ${response.expected.Capacity} ${response.expected.Type}</p>
                <p>Found: ${response.actual.Capacity} ${response.actual.Type}</p>
            `;
            showModal({ title: 'Check-in Error: Mismatch' }, content);
        } else if (response.error === 'checked-in') {
            const content = `
                <p><strong>That part is already checked-in:</strong></p>
                <p>Serial number: ${partSn}</p>
            `;
            showModal({ title: 'Check-in Error: Already checked-in.' }, content);
        } else if (response.error === 'not_in_inventory') {
            const content = `
                <p><strong>That part has never been added to inventory.</strong></p>
                <p>Serial number: ${partSn}</p>
                <p>Add item to inventory. Fill in the blanks</p>
            `;
            showModal({ title: 'Check-in Error: Part not found in inventory.' }, content);
        } else if (response.error === 'missing_serial_number') {
            // New case for missing serial number
            const content = `
                <p><strong>Unit Serial Number is missing:</strong></p>
                <p>Please provide a valid Unit Serial Number for part: ${partSn}.</p>
            `;
            showModal({ title: 'Check-in Error: Missing Serial Number' }, content);
        }
    }
    
    
    function checkOutPart(dataObject) {
        dataObject.parts.forEach((part, index) => {
            const partSn = dataObject.serial_numbers[index];  // Get the serial number for the current part
            const unitSn = dataObject.unit_sn;  // Get the Unit Serial Number
    
            // Validate if Unit Serial Number is missing
            if (!unitSn) {
                const content = `
                    <p><strong>Unit Serial Number is missing.</strong></p>
                    <p>Please provide a valid serial number for part: ${partSn}.</p>
                `;
                showModal({ title: 'Error: Missing Unit Serial Number' }, content);
                return;  // Prevent further execution for this part
            }
    
            // Prepare the data to be sent to the server including Type and Capacity
            const partData = {
                Part_sn: partSn,
                Type: part.type,
                Capacity: part.capacity,
                Size: dataObject.size,
                Speed: dataObject.Speed,
                Part_status: 'Out',
                Unit_sn: unitSn,  // Include the valid Unit Serial Number here
                Note: dataObject.note
            };
    
            $.ajax({
                url: '/check_part_in_inventory',  // Server-side script to check the inventory
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(partData),
                success: function (response) {
                    if (response.exists) {
                        // If part exists and matches type and capacity, update its status to 'Out'
                        $.ajax({
                            url: '/update_part_status',
                            type: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                Part_sn: partSn,
                                TID: dataObject.tid,
                                Unit_sn: unitSn,  // Include Unit Serial Number here
                                Part_status: 'Out',
                                Note: dataObject.note
                            }),
                            success: function (updateResponse) {
                                // Refreshes the page after checking out
                                partsTable.ajax.reload(null, false);
                            },
                            error: function (err) {
                                console.error("Error updating part status: ", err);
                            }
                        });
                    } else {
                        // If part does not exist or does not match, show modal to handle errors
                        handleCheckOutErrors(response, partSn, partData);
                    }
                },
                error: function (err) {
                    console.error("Error checking part out inventory: ", err);
                    alert('Error checking part out inventory: ' + err.responseText);
                }
            });
        });
    }
    
    // New function to handle edge case errors during check-out
    function handleCheckOutErrors(response, partSn, partData) {
        if (response.error === 'size_mismatch') {
            const content = `
                <p><strong>Size mismatch detected:</strong></p>
                <p>Expected: ${response.expected.Size}</p>
                <p>Provided: ${response.actual.Size}</p>
                <p>Please correct the Size.</p>
            `;
            showModal({ title: 'Check-out Error: Size Mismatch' }, content);
        } else if (response.error === 'mismatch') {
            const content = `
                <p><strong>Mismatch detected:</strong></p>
                <p>Expected: ${response.expected.Capacity} ${response.expected.Type}</p>
                <p>Found: ${response.actual.Capacity} ${response.actual.Type}</p>
            `;
            showModal({ title: 'Check-out Error: Mismatch in type or capacity.' }, content);
        } else if (response.error === 'checked-out') {
            let speedField = '';  // Speed field isn't needed for HD or SSD
    
            if (!["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type)) {
                speedField = `
                    <div style="flex: 1; padding: 8px;">Speed</div>
                `;
            }
    
            const speedValue = !["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type) ? `
                <div style="flex: 1; padding: 8px;">${response.part.Speed}</div>
            ` : '';
            const content = `
                <p><strong>That part is already checked-out.</strong></p>
                <p>Serial number: ${partSn}</p>
                <div class="modal-table-wrapper">
                    <div class="modal-table-header">
                        <div style="flex: 1; padding: 8px;">Type</div>
                        <div style="flex: 1; padding: 8px;">Capacity</div>
                        <div style="flex: 1; padding: 8px;">Size</div>
                        ${speedField}
                        <div style="flex: 1; padding: 8px;">Brand</div>
                        <div style="flex: 1; padding: 8px;">Model</div>
                        <div style="flex: 1; padding: 8px;">Location</div>
                    </div>
                    <div style="display: flex;">
                        <div style="flex: 1; padding: 8px;">${response.part.Type}</div>
                        <div style="flex: 1; padding: 8px;">${response.part.Capacity}</div>
                        <div style="flex: 1; padding: 8px;">${response.part.Size}</div>
                        ${speedValue}
                        <div style="flex: 1; padding: 8px;">${response.part.Brand}</div>
                        <div style="flex: 1; padding: 8px;">${response.part.Model}</div>
                        <div style="flex: 1; padding: 8px;">${response.part.Location}</div>
                    </div>
                </div>
            `;
            showModal({ title: 'Check-out Error: Already checked-out.' }, content);
        } else if (response.error === 'not_in_inventory') {
            let speedField = '';  // Speed field isn't needed for HD or SSD
    
            if (!["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type)) {
                speedField = `
                    <div style="flex: 1; padding: 8px;">Speed</div>
                `;
            }
    
            const speedInput = !["HD", "SSD", "3.5\" HD", "2.5\" HD"].includes(partData.Type) ? `
                <div style="flex: 1; padding: 8px;">
                    <input type="text" id="iSpeed" name="Speed" style="width: 100%;" />
                </div>
            ` : '';
            const content = `
                <p><strong>That part has never been added to inventory.</strong></p>
                <p>Serial number: ${partSn}</p>
                <p>Add item to inventory. Fill in the blanks.</p>
                <div class="modal-table-wrapper">
                    <div class="modal-table-header">
                        <div style="flex: 1; padding: 8px;">Type</div>
                        <div style="flex: 1; padding: 8px;">Capacity</div>
                        <div style="flex: 1; padding: 8px;">Size</div>
                        ${speedField}
                        <div style="flex: 1; padding: 8px;">Brand</div>
                        <div style="flex: 1; padding: 8px;">Model</div>
                        <div style="flex: 1; padding: 8px;">Location</div>
                        <div style="flex: 1; padding: 8px;">Part SN</div>
                    </div>
                    <div style="display: flex;">
                        <div style="flex: 1; padding: 8px;">
                            <input type="text" id="iType" name="Type" style="width: 100%;" value="${partData.Type}" />
                        </div>
                        <div style="flex: 1; padding: 8px;">
                            <input type="text" id="iCapacity" name="Capacity" style="width: 100%;" value="${partData.Capacity}" />
                        </div>
                        <div style="flex: 1; padding: 8px;">
                            <input type="text" id="ddSize" name="Size" style="width: 100%;" value="${partData.Size}" />
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
                            <input type="text" id="iPart_sn" name="Part SN" style="width: 100%;" value="${partSn}" />
                        </div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <button type="button" id="add_btn" class="btn btn-primary mb-2">Add Part</button>    
                </div>
            `;
            showModal({ title: 'Check-out Error: Part not found in inventory.' }, content);
    
            // Handle form submission when the user clicks "Add Part"
            $('#add_btn').click(function () {
                const newPartData = {
                    TID: '',
                    Unit_sn: '',
                    Part_status: 'Out',
                    Note: 'New part added to inventory',
                    Type: $('#iType').val(),
                    Capacity: $('#iCapacity').val(),
                    Size: $('#ddSize').val(),
                    Speed: $('#iSpeed').val(),
                    Brand: $('#iBrand').val(),
                    Model: $('#iModel').val(),
                    Location: $('#iLocation').val(),
                    Part_sn: $('#iPart_sn').val()
                };
                submitPart(newPartData);
            });
        }
    }
    