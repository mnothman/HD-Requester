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
            toggleNotesBtn.classList.add('notes-active');
        } else {
            notesContainer.style.display = "none";
            toggleNotesBtn.classList.remove('notes-active'); 
            textarea.value = ""; // Clear the textarea when hiding
        }
    };

    // Sidebar toggle functionality
    const hamburgerBtn = $('#hamburgerBtn');
    const sidebar = $('#sidebar');

    hamburgerBtn.on('click', function() {
        sidebar.toggleClass('active');
    }); 
     
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
        if (parsedData == null) {
            console.log("Error unable to proceed with request")
            return;
        }
        // IN or OUT
        var action = document.querySelector('.btn-active').innerText;
        if (action) {
            checkPartsInInventory(parsedData, action);
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

    // Handle right-click on table row
    // Prevent the default right-click context menu
    $('#partsTable tbody').on('contextmenu', 'tr', function (e) {
        e.preventDefault();   
        // Get the part data from the row
        const partData = $(this).children("td").map(function () {
            return $(this).text();
        }).get();

        // Show context menu at mouse position
        $(".context-menu").css({
            display: "block",
            left: e.pageX + "px",
            top: e.pageY + "px"
        // Attach part data to the context menu    
        }).data('partData', partData); 
    });

    // Hide context menu when clicking elsewhere
    $(document).on("click", function () {
        $(".context-menu").hide();
    });

    // Handle clicking "Edit" in the context menu
    $(".context-menu .edit").on("click", function () {
        const partData = $(".context-menu").data('partData');

        // Generate modal content dynamically to match the design of other modals
        const modalContent = `
            <form id="editPartForm">
                <div class="form-group">
                    <label for="editType">Type:</label>
                    <input type="text" id="editType" class="form-control" value="${partData[0]}" required>
                </div>
                <div class="form-group">
                    <label for="editCapacity">Capacity:</label>
                    <input type="text" id="editCapacity" class="form-control" value="${partData[1]}" required>
                </div>
                <div class="form-group">
                    <label for="editSize">Size:</label>
                    <input type="text" id="editSize" class="form-control" value="${partData[2]}" required>
                </div>
                <div class="form-group">
                    <label for="editSpeed">Speed:</label>
                    <input type="text" id="editSpeed" class="form-control" value="${partData[3]}">
                </div>
                <div class="form-group">
                    <label for="editBrand">Brand:</label>
                    <input type="text" id="editBrand" class="form-control" value="${partData[4]}" required>
                </div>
                <div class="form-group">
                    <label for="editModel">Model:</label>
                    <input type="text" id="editModel" class="form-control" value="${partData[5]}" required>
                </div>
                <div class="form-group">
                    <label for="editLocation">Location:</label>
                    <input type="text" id="editLocation" class="form-control" value="${partData[6]}">
                </div>
                <div class="form-group">
                    <label for="editPart_sn">Part Serial Number:</label>
                    <input type="text" id="editPart_sn" class="form-control" value="${partData[7]}" readonly>
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <button type="button" class="btn btn-secondary" id="closeModalBtn">Cancel</button>
            </form>
        `;

        //Show the modal using the general purpose modal system
        showModal({ title: 'Edit Part' }, modalContent);

        // Attach form submission handler
        $(document).on('submit', '#editPartForm', function (e) {
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
                    alert(response.message);
                    partsTable.ajax.reload(null, false);
                },
                error: function (xhr, status, error) {
                    alert("Error Updating Part: " + error);
                }
            });

            //Close the Modal after submission 
            $('#Modal').css('display', 'none');
        });

        // Add Cancel button functionality
        $(document).on('click', '#closeModalBtn', function () {
            $('#Modal').css('display', 'none');
        });

        // Hide the context menu
        $(".context-menu").hide();
    });
    
});

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
            technology: null,
            note: noteContent
        };
    
        if (lines.length < 4) { // Minimum number of lines for valid input
            console.error("Error: Insufficient input data.");
            // Show modal for missing or invalid Unit Serial Number
            const content = `
                <p><strong>Missing Information For Request</strong></p>
                <p>Please provide a valid request to proceed.</p>
            `;
            showModal({ title: 'Error: Insufficient input data.' }, content);
            return null; // Stop further processing
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
        if (!dataObject.unit_sn || isNaN(dataObject.unit_sn) || dataObject.unit_sn.length < 5) {
            // Show modal for missing or invalid Unit Serial Number
            const content = `
                <p><strong>Unit Serial Number is missing or invalid.</strong></p>
                <p>Please provide a valid Unit Serial Number to proceed.</p>
            `;
            showModal({ title: 'Error: Missing Unit serial number' }, content);
            return null; // Stop further processing
        }
    
        // Parse Parts
        var i = 2;
        while (lines[i] && !["Laptop", "Desktop", "Server", "AiO"].includes(lines[i].trim())) {
            var details = lines[i].trim().split(' ');
            var part = {
                Part_sn: null,
                Type: null,
                Capacity: null,
                Size: null,
                Speed: null
            };
    
            // Extract capacity and type information
            if (details[0].match(/\d+(GB|TB)$/)) {
                part.Capacity = details[0];
                part.Type = details.slice(1).join(' ');
            } else {
                var capacityIndex = details.findIndex(detail => detail.match(/\d+(GB|MB)$/));
                if (capacityIndex !== -1) {
                    part.Type = details.slice(0, capacityIndex).join(' ');
                    part.Capacity = details[capacityIndex];
                } else {
                    part.Type = details.join(' '); // If no capacity found, consider everything as type
                }
            }

            dataObject.parts.push(part);
            i++;
        }
    
        // Parse Size (Technology)
        if (lines.length == i) {
            // Show modal for missing or invalid Unit size
            const content = `
                <p><strong>Missing or invalid Unit size.</strong></p>
                <p>Please provide a valid Unit Size to proceed.</p>
            `;
            showModal({ title: 'Error: Missing Unit Size' }, content);
            return null; // Stop further processing
        }
    
        dataObject.technology = lines[i].trim();

        // Assign Size for Parts if applicable
        if (dataObject.technology) {
            dataObject.parts.forEach(part => {
                if (['PC3', 'PC3L', 'PC4'].includes(part.Type)) {
                    if (dataObject.technology === 'Server') {
                        part.Size = 'Desktop';
                    } else if (dataObject.technology === 'AiO') {
                        part.Size = 'Laptop';
                    } else {
                        part.Size = dataObject.technology;
                    }
                }
            });
        }

        i++;
    
        // Parse Serial Numbers and Assign to Parts
        var partIndex = 0;
        while (i < lines.length && partIndex < dataObject.parts.length) {
            var serialNumber = lines[i].trim();
            dataObject.parts[partIndex].Part_sn = serialNumber;
            partIndex++;
            i++;
        }
    
        // Check if number of parts matches number of serial numbers
        if (partIndex !== dataObject.parts.length) {
            console.error("Error: The number of parts does not match the number of serial numbers.");
            alert('Error: The number of parts does not match the number of serial numbers.');
            return null;
        }
    
        return dataObject;
        /*** parseTextInput dataObject structure - RC ***/
        /* 
            tid: null,
            unit_sn: null,
            parts: [{
                Part_sn: null,
                Type: null,
                Capacity: null,
                Size: null,
                Speed: null,
            }],
            technology: null
            note: noteContent
        */

    }
    // end parseTextInput
    
    
    function makeDivTable(partHTML, location) {
        let table = `
            <div class="modal-table-wrapper">
                <div class="modal-table-header">
                    <div class="mt-cell">Type</div>
                    <div class="mt-cell">Capacity</div>
                    <div class="mt-cell">Size</div>
                    <div class="mt-cell">Speed</div>
                    <div class="mt-cell">Brand</div>
                    <div class="mt-cell">Model</div>`;
        if(location) {
            table += `<div class="mt-cell">Location</div>`
        }
        table += `<div class="mt-cell">Part SN</div>
                </div>
                ${partHTML}
            </div>
            `;
        return table;
    }

    function checkPartsInInventory(partsData, action) {

        console.log("Data object received:", partsData);
        partsData["action"] = action
        const edgeCases = {
            "mismatchSize": { part: [] },
            "missingType": { part: [] },
            "mismatchType": { part: [] },
            "missingCapacity": { part: [] },
            "mismatchCapacity": { part: [] },
            "alreadyCheckedIn": { part: [] },
            "alreadyCheckedOut": { part: [] },
            "doesntExist": { part: [] }
        };
        


        // simple checks before server 
        // partsData is the "parsedData" object from parseTextInput()
        partsData.parts.forEach((part, index) => {

            // Edge Cases: Check for missing Capacity or Type
            if (!part['Capacity'] || part['Capacity'] === '') {
                edgeCases["missingCapacity"]["part"].push({
                    Part_sn: part.Part_sn,
                });
            }
            if (!part['Type'] || part['Type'] === '') {
                edgeCases["missingType"]["part"].push({
                    Part_sn: part.Part_sn,
                });
            }
        });

        console.log("Found these edge cases: ", edgeCases);

        $.ajax({
            url: '/check_part_in_inventory',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(partsData),
            success: function (response) {

                // Copy key-value pairs from the response's `partsEdgeCases` to `edgeCases`
                Object.keys(response).forEach(key => {
                    if (response[key] && response[key].part) {
                        edgeCases[key].part = response[key].part;
                    }
                });

                if (edgeCases.mismatchSize.part.length > 0) {
                    console.log("Mismatch Size");
                }
                if (edgeCases.mismatchType.part.length > 0) {
                    console.log("Mismatch Type");
                }
                if (edgeCases.mismatchCapacity.part.length > 0) {
                    console.log("Mismatch Capacity");
                }
                if (edgeCases.alreadyCheckedIn.part.length > 0) {
                    console.log("Already Checked In");
                }
                if (edgeCases.alreadyCheckedOut.part.length > 0) {
                    console.log("Already Checked Out");
                }
                if (edgeCases.doesntExist.part.length > 0) {
                    console.log("Doesn't Exist");
                }
                let modalTitle = "Check-" + (action === 'OUT' ? "Out" : "In") + " Error:";
                let modalContent = "";
                let partHTML = "";

                 // Append HTML for each edge case
                for (const [edgeCase, value] of Object.entries(edgeCases)) {
                    if (value.part.length > 0) {
                        switch (edgeCase) {
                            case "mismatchSize":
                                modalContent += "<h3>Size mismatch detected</h3>";
                                value.part.forEach(part => {
                                    modalContent += `<p><strong>Type: </strong>${part.Type}<br><strong>Requested: </strong>${part["requestedSize"]}<br><strong>Actual: </strong>${part.Size}<br>Serial number: ${part.Part_sn}<br></p>`;
                                });
                                break;
                            case "mismatchType":
                                modalContent += "<h3>Type mismatch detected</h3>";
                                value.part.forEach(part => {
                                    modalContent += `<p><strong>Actual: </strong>${part.Type}<br><strong>Requested: </strong>${part["requestedType"]}<br>Serial number: ${part.Part_sn}<br></p>`;
                                });
                                break;
                            case "mismatchCapacity":
                                modalContent += "<h3>Capacity mismatch detected</h3>";
                                value.part.forEach(part => {
                                    modalContent += `<p><strong>Requested: </strong>${part.requestedCapacity}<br><strong>Actual: </strong>${part.Capacity}<br>Serial number: ${part.Part_sn}<br></p>`;
                                });
                                break;
                            case "missingType":
                                modalContent += "<h3>Missing Part Type</h3>";
                                value.part.forEach(part => {
                                    modalContent += `<p><h4 id="error-message">Please provide a valid type for this part.</h4>Serial Number: ${part.Part_sn}</p>`;
                                });
                                break;
                            case "missingCapacity":
                                modalContent += "<h3>Missing Part Capacity</h3>";
                                value.part.forEach(part => {
                                    modalContent += `<p><h4 id="error-message">Please provide a valid capacity for this part.</h4>Serial Number: ${part.Part_sn}</p>`;
                                });
                                break;
                            case "alreadyCheckedIn":
                                modalContent += `<h3>Already Checked In</h3>`;
                                modalContent += `<h4 id="error-message">The following parts are already checked in:</h4>`
                                partHTML = "";
                                value.part.forEach(part => {
                                    partHTML += `<div style="display: flex;">
                                    <div class="mt-cell">${part.Type}</div>
                                    <div class="mt-cell">${part.Capacity}</div>
                                    <div class="mt-cell">${part.Size}</div>
                                    <div class="mt-cell">${part.Speed}</div>
                                    <div class="mt-cell">${part.Brand}</div>
                                    <div class="mt-cell">${part.Model}</div>
                                    <div class="mt-cell">${part.Location}</div>
                                    <div class="mt-cell">${part.Part_sn}</div>
                                    </div>`;
                                });
                                modalContent += makeDivTable(partHTML, true);

                                break;
                            case "alreadyCheckedOut":
                                modalContent += "<h3>Already Checked Out</h3>";
                                modalContent += `<h4 id="error-message">The following parts are already checked out:</h4>`;
                                partHTML = ''; // reset
                                value.part.forEach(part => {
                                    partHTML += `<div style="display: flex;">
                                    <div class="mt-cell">${part.Type}</div>
                                    <div class="mt-cell">${part.Capacity}</div>
                                    <div class="mt-cell">${part.Size}</div>
                                    <div class="mt-cell">${part.Speed}</div>
                                    <div class="mt-cell">${part.Brand}</div>
                                    <div class="mt-cell">${part.Model}</div>
                                    <div class="mt-cell">${part.Part_sn}</div>
                                    </div>`;
                                });
                                modalContent += makeDivTable(partHTML, false);
                                break;
                            case "doesntExist":
                                modalContent += `<h3>Part Doesn't Exist in Inventory</h3><h4 id="error-message">Add item to inventory. Fill in the blanks.</h4>`;
                                partHTML = ''; // reset
                                value.part.forEach(part => {  
                                    partHTML += `<div style="display: flex;">
                                        <div class="mt-cell">
                                            <input type="text" id="iType_${part.Part_sn}" name="Type" style="width: 100%;" value="${part.Type}"/>
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iCapacity_${part.Part_sn}" name="Type" style="width: 100%;" value="${part.Capacity}"/>
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="ddSize_${part.Part_sn}" name="Type" style="width: 100%;" value="${part.Size}"/>
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iSpeed_${part.Part_sn}" name="Speed" style="width: 100%;" />
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iBrand_${part.Part_sn}" name="Brand" style="width: 100%;" />
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iModel_${part.Part_sn}" name="Model" style="width: 100%;" />
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iLocation_${part.Part_sn}" name="Location" style="width: 100%;" />
                                        </div>
                                        <div class="mt-cell">
                                            <input type="text" id="iPart_sn_${part.Part_sn}" name="Part SN" style="width: 100%;" value="${part.Part_sn}"/>
                                        </div>  
                                    </div>
                                `});
                                modalContent += makeDivTable(partHTML, true);
                                modalContent += `
                                <div style="margin-top: 10px;">
                                    <button type="button" id="add_btn" class="btn btn-primary mb-2">Add Part</button>	
                                </div>
                                `;
                                // Handle form submission when the user clicks "Add Part"
                                $('#add_btn').click(function () {
                                    const newPartData = {
                                        TID: '',
                                        Unit_sn: '',
                                        Part_status: 'Out',
                                        Note: 'New part added to inventory',
                                        Type: $(`#iType_${part.Part_sn}`).val(),
                                        Capacity: $(`#iCapacity_${part.Part_sn}`).val(),
                                        Size: $(`#ddSize_${part.Part_sn}`).val(),
                                        Speed: $(`#iSpeed_${part.Part_sn}`).val(),
                                        Brand: $(`#iBrand_${part.Part_sn}`).val(),
                                        Model: $(`#iModel_${part.Part_sn}`).val(),
                                        Location: $(`#iLocation_${part.Part_sn}`).val(),
                                        Part_sn: $(`#iPart_sn_${part.Part_sn}`).val()
                                    };
                                    submitPart(newPartData);
                                });
                                break;
                            default:
                                modalTitle = "Unknown Edge Case";
                            }
                        }
                    }

                    // Show the modal
                    if (modalContent) {
                        
                        showModal({ title: modalTitle }, modalContent);
                    }
                }
            
        });

    }