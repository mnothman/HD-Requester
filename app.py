from flask import Blueprint, current_app, Flask, g, jsonify, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
from argon2 import PasswordHasher, Type
import re, sqlite3

app = Flask(__name__)

app.secret_key = 'key'

# Use argon2id for better security
ph = PasswordHasher(type=Type.ID)


db_blueprint = Blueprint('db', __name__)
DATABASE = 'refresh.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@db_blueprint.teardown_app_request
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    current_app.logger.info("Database is connected")

@app.route('/')
def index():
    admin_cookie = request.cookies.get('admin')
    if admin_cookie == 'true':
        return render_template('index.html', logged_in=True)
    else:
        return render_template('index.html', logged_in=False)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('remember_me')  # Get the remember_me checkbox value

        conn = get_db()
        cursor = conn.cursor()

        # Fetch the hashed password from the database
        cursor.execute("SELECT password FROM Admin WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            try:
                # Verify the password using Argon2id
                if ph.verify(user['password'], password):
                    print("Password verified successfully!")
                    response = make_response(redirect(url_for('dashboard')))
                    response.set_cookie('admin_logged_in', 'true', max_age=3600)  # Expires in 1 hour

                    # Set the remember_me cookie if the checkbox is checked
                    if remember_me:
                        print(f"Setting remember_me cookie for username: {username}")
                        response.set_cookie('remember_me', username, max_age=30*24*60*60)  # Expires in 30 days
                    else:
                        # Clear the remember_me cookie if not checked
                        print("Clearing remember_me cookie")
                        response.set_cookie('remember_me', '', expires=0)

                    return response
                else:
                    print("Password verification failed.")
                    flash('Invalid username or password')
                    
                    return redirect(url_for('login'))
            except Exception as e:
                print(f"Verification error: {e}")
                flash('Invalid username or password')
                return redirect(url_for('login'))
        else:
            print("User not found.")
            flash('User not found')
            return redirect(url_for('login'))

    # Handle GET request: Check if the admin is already logged in
    if request.cookies.get('admin_logged_in'):
        return redirect(url_for('dashboard'))  # Redirect if already logged in

    # If not logged in, check if "remember_me" exists to pre-fill the login form
    remember_me_username = request.cookies.get('remember_me')
    return render_template('login.html', remember_me=remember_me_username)



@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))  # Redirect to the homepage
    
    # Remove the session cookie that tracks login state
    response.set_cookie('admin_logged_in', '', expires=0)

    # Do not delete the remember_me cookie, so it remains for future login pre-filling

    return response



# Admin Dashboard route
@app.route('/dashboard')
def dashboard():
    parts = record()
    # Check if the user is logged in by checking the 'admin_logged_in' cookie
    if request.cookies.get('admin_logged_in'):
        return render_template('dashboard.html',parts=parts)  # Render dashboard page
    else:
        # If not logged in, redirect back to login page
        return redirect(url_for('login'))


def record():
    db = get_db()
    query = '''
SELECT l.Date_time, 
           CASE 
               WHEN l.Part_status = 'In' THEN 'Check In' 
               WHEN l.Part_status = 'Out' THEN 'Check Out' 
               ELSE 'Unknown' 
           END AS Action,
           l.TID, 
           l.Unit_sn, 
           p.Type, 
           p.Capacity, 
           p.Size, 
           p.Speed, 
           p.Brand, 
           p.Model, 
           l.Part_sn,
           l.Note
    FROM Log l 
    JOIN Part p ON l.Part_sn = p.Part_sn 
    ORDER BY l.Date_time DESC
    '''
    parts = db.execute(query).fetchall()
    return parts

# Recover Password route Step 1
@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        # Handle the form submission (POST)
        return check_answers()  # This function should handle form validation and verification
    else:
        # Render the form (GET)
        return render_template('recover-password.html')

# Security Question Check Step 2
@app.route('/check_answers', methods=['POST'])
def check_answers():
    answer1 = request.form['answer1']
    answer2 = request.form['answer2']
    answer3 = request.form['answer3']

    # Simulated logic to check answers, replace with actual DB logic
    stored_answers = {
        'answer1': 'Kings',
        'answer2': 'Pet',
        'answer3': 'Hawaii'
    }

    if answer1 == stored_answers['answer1'] and answer2 == stored_answers['answer2'] and answer3 == stored_answers['answer3']:
        return jsonify({'success': True, 'message': 'Answers correct, please set a new password.'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect answers, please try again.'})

# Reset Password Endpoint Step 3
@app.route('/reset_password', methods=['POST'])
def reset_password():
    new_password = request.form['new_password']

    # Hash the new password with Argon2
    hashed_password = ph.hash(new_password)

    # Update the Admin table with the hashed password
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Update the password in the Admin table (assuming only one admin user)
        cursor.execute("UPDATE Admin SET password = ? WHERE username = ?", (hashed_password, 'admin'))  # Update 'admin'
        conn.commit()

        return jsonify({'success': True, 'message': 'Password has been updated successfully.'})
    except sqlite3.Error as e:
        # If an error occurs, rollback the transaction and send an error message
        conn.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while updating the password: ' + str(e)})
    finally:
        conn.close()



@app.route('/get_parts', methods=['POST'])
def get_parts():
    parts = get_all_parts()  # Fetch all parts
    return jsonify({
        'status': 'success',
        'data': [dict(part) for part in parts]  # Convert to list of dictionaries
    })


from datetime import datetime
from flask import jsonify, request
import sqlite3

@app.route('/update_part', methods=['POST'])
def update_part():
    data = request.get_json()
    print("Received data for update:", data)  # Debug print to verify received data

    part_sn = data.get('part_sn')
    if not part_sn:
        return jsonify({'status': 'error', 'message': 'No part serial number provided'}), 400

    # Proceed to check the part in the database and update it if found
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Fetch the existing part details
        print("Checking")
        part = cursor.execute("SELECT * FROM Part WHERE Part_sn = ?", (part_sn,)).fetchone()
        if not part:
            return jsonify({'status': 'error', 'message': 'Part NOT FOUND'}), 404

        # Mapping the fetched part to its attributes for comparison
        old_data = {
            'type': part['Type'],
            'capacity': part['Capacity'],
            'size': part['Size'],
            'speed': part['Speed'],
            'brand': part['Brand'],
            'model': part['Model'],
            'location': part['Location']
        }
        print(part['Capacity'])

        # Constructing the note for changes
        changes = []
        for key in old_data:
            if old_data[key] != data[key]:
                changes.append(f"{key} changed from '{old_data[key]}' to '{data[key]}'")
        note = "; ".join(changes) if changes else ""

        # Update the part in the Part table
        cursor.execute('''
            UPDATE Part SET Type = ?, Capacity = ?, Size = ?, Speed = ?, Brand = ?, Model = ?, Location = ?
            WHERE Part_sn = ?
        ''', (
            data['type'],   # Match with the keys used in `index.js`
            data['capacity'],
            data['size'],
            data['speed'],
            data['brand'],
            data['model'],
            data['location'],
            part_sn
        ))

        # Log the update in the Log table
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time, Note)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            None,           # Assuming TID can be NULL as requested
            None,           # Assuming Unit_sn is optional here
            part_sn,
            data.get('Part_status', 'in'),  # Default to 'in' if Part_status is not provided
            timestamp,
            note
        ))

        conn.commit()
        print("Part updated successfully")  # Debug confirmation
        return jsonify({'status': 'success', 'message': 'Part updated successfully'})
    except sqlite3.Error as e:
        conn.rollback()
        print("Error during update:", str(e))  # Log any errors
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()



def get_all_parts(search_type=None):
    db = get_db()
    query = 'SELECT * FROM Part WHERE Status IS "In"'
    args = ()
    if search_type:
        query += ' AND Type LIKE ?'
        args = ('%' + search_type + '%',)
    parts = db.execute(query, args).fetchall()
    return parts

@app.route('/get_inventory', methods=['GET'])
def get_inventory():
    try:
        # Fetch inventory summary from the database
        inventory = get_inventory_db()
        # Convert the result for JSON
        inventory_list = [dict(row) for row in inventory]
        return jsonify(inventory_list)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_inventory_db():
    db = get_db()
    query = '''
        SELECT
            p.Type,
            p.Size,
            COUNT(*) AS quantity
        FROM
            Part p
        GROUP BY
            p.Type,
            p.Size
    '''
    try:
        # Execute the query and fetch all results
        result = db.execute(query).fetchall()
        return result
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {str(e)}")


@app.route('/get_part_capacities', methods=['GET'])
def get_part_capacities():
    type = request.args.get('type')
    size = request.args.get('size')
    db = get_db()
    query = '''
        SELECT DISTINCT Capacity FROM Part
        WHERE Type = ?
    '''
    if size == "null":
        query = '''
            SELECT DISTINCT Capacity FROM Part
            WHERE Type = ? AND Size IS NULL
        '''
        params = (type, )
    else:
        query = '''
            SELECT DISTINCT Capacity FROM Part
            WHERE Type = ? AND Size = ?
        '''
        params = (type, size)
    try:
        result = db.execute(query, params).fetchall()
        capacities = [row['Capacity'] for row in result]
        return jsonify(capacities)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_part_count', methods=['GET'])
def get_part_count():
    part_type = request.args.get('type')
    capacity = request.args.get('capacity')
    db = get_db()

    query = '''
        SELECT COUNT(*) AS count FROM Part
        WHERE Type = ? AND Capacity = ?
    '''
    try:
        result = db.execute(query, (part_type, capacity)).fetchone()
        count = result['count']
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/inventory')
def inventory():
    return render_template('temp_inventory.html')

# Database function to insert a part
def insert_part(part_data):
    # Connection to SQLite database
    conn = get_db()
    cursor = conn.cursor()

    try:
        part_sn = part_data['Part_sn']
        tid = part_data['TID']
        unit_sn = part_data['Unit_sn']
        part_status = part_data['Part_status']  # update the part status given
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        note = part_data['Note']
        # SQL query to insert a new part into the Part table
        conn.execute('BEGIN')
        cursor.execute('''
            INSERT INTO Part (Part_sn, Type, Capacity, Size, Speed, Brand, Model, Location, Status, timedate_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (part_data['Part_sn'], part_data['Type'], part_data['Capacity'], part_data['Size'], part_data['Speed'],
              part_data['Brand'], part_data['Model'], part_data['Location'], 'In', timestamp))
        
        # Insert a new log entry with the current timestamp
        cursor.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time, Note) VALUES (?, ?, ?, ?, ?, ?)', 
                     (tid, unit_sn, part_sn, part_status, timestamp, note))

        # Commit the changes
        conn.commit()

    except sqlite3.IntegrityError as e:
        print("Error occurred: ", e)
        # Handle specific integrity errors, e.g., unique constraint failed
        conn.rollback()  # Rollback the transaction on error
        return {'status': 'error', 'message': str(e)}

    except Exception as e:
        print("Error occurred: ", e)
        conn.rollback()  # Ensure no partial data is written
        return {'status': 'error', 'message': str(e)}

    finally:
        conn.close()  # Always close the connection

    return {'status': 'success', 'message': 'Part added successfully and logged as In'}

# Function for getting data to display trends
@app.route('/get_trends', methods=['GET'])
def get_trends():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    # Check for complete parameters
    if not month or not year:
        return jsonify({'status': 'error', 'message': 'Month and year are required.'}), 400

    # For query range, first_day included and last_day excluded 
    first_day = datetime(year, month, 1)    # Sets first day of specified month 
    last_day = datetime(year + (1 if month == 12 else 0), (month % 12) + 1, 1)  # Calculates the first day of the next month and wraps if needed 

    db = get_db()
    query = '''
    SELECT 
        DATE(Date_time) AS date, 
        COUNT(CASE WHEN Part_status = 'In' THEN 1 END) AS check_ins,
        COUNT(CASE WHEN Part_status = 'Out' THEN 1 END) AS check_outs,
        COUNT(CASE WHEN Size = 'Laptop' THEN 1 END) AS laptop_transactions,
        COUNT(CASE WHEN Size = 'Desktop' THEN 1 END) AS desktop_transactions
        FROM Log l
        JOIN Part p ON l.Part_sn = p.Part_sn
        WHERE Date_time >= ? AND Date_time < ?
        GROUP BY DATE(Date_time)
        ORDER BY DATE(Date_time)
    '''

    try:
        results = db.execute(query, (first_day, last_day)).fetchall()
        trends = {row['date']: {
            'check_ins': row['check_ins'],
            'check_outs': row['check_outs'],
            'laptop_transactions': row['laptop_transactions'],
            'desktop_transactions': row['desktop_transactions']
        } for row in results}

        return jsonify({'status': 'success', 'data': trends})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Function to get data regarding upgrades
@app.route('/get_upgrades', methods=['GET'])
def get_upgrades():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    if not month or not year:
        return jsonify({'status': 'error', 'message': 'Month and year are required.'}), 400

    first_day = datetime(year, month, 1)
    last_day = datetime(year + (1 if month == 12 else 0), (month % 12) + 1, 1)

    db = get_db()
    query = '''
    SELECT 
        DATE(Date_time) AS date, 
        Unit_sn,
        Type,
        Capacity,
        COUNT(CASE WHEN Part_status = 'In' THEN 1 END) AS check_ins,
        COUNT(CASE WHEN Part_status = 'Out' THEN 1 END) AS check_outs
    FROM Log l
    JOIN Part p ON l.Part_sn = p.Part_sn
    WHERE Date_time >= ? AND Date_time < ?
    GROUP BY date, Unit_sn, Type, Capacity
    HAVING COUNT(DISTINCT Capacity) > 1  
        AND (COUNT(CASE WHEN Part_status = 'In' THEN 1 END) > 0 
            OR COUNT(CASE WHEN Part_status = 'Out' THEN 1 END) > 0)
    ORDER BY date, Unit_sn, Type, Capacity
    '''

    try:
        results = db.execute(query, (first_day, last_day)).fetchall()
        upgrades = {}

        for row in results:
            date = row['date']
            unit_sn = row['Unit_sn']
            part_type = row['Type']
            capacity = row['Capacity']

            if date not in upgrades:
                upgrades[date] = {}

            if unit_sn not in upgrades[date]:
                upgrades[date][unit_sn] = {}

            if part_type not in upgrades[date][unit_sn]:
                upgrades[date][unit_sn][part_type] = {}

            if capacity in upgrades[date][unit_sn][part_type]:
                upgrades[date][unit_sn][part_type][capacity]['check_ins'] += row['check_ins']
                upgrades[date][unit_sn][part_type][capacity]['check_outs'] += row['check_outs']
            else:
                upgrades[date][unit_sn][part_type][capacity] = {
                    'check_ins': row['check_ins'],
                    'check_outs': row['check_outs']
                }

        return jsonify({'status': 'success', 'data': upgrades})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Function to get data regarding repeated upgrades
@app.route('/get_repeated', methods=['GET'])
def get_repeated():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    if not month or not year:
        return jsonify({'status': 'error', 'message': 'Month and year are required.'}), 400

    start_date = datetime(year, month + 1, 1)
    end_date = datetime(year - 1, month, 1)
    
    db = get_db()
    check_in_query = '''
        SELECT Unit_sn, MAX(Date_time) AS last_request_date, COUNT(*) AS check_count
        FROM Log
        WHERE Date_time >= ? AND Date_time < ? AND Part_status = 'In'
        GROUP BY Unit_sn
        HAVING COUNT(*) > 1;
        '''
    check_out_query = '''
        SELECT Unit_sn, MAX(Date_time) AS last_request_date, COUNT(*) AS check_count
        FROM Log
        WHERE Date_time >= ? AND Date_time < ? AND Part_status = 'Out'
        GROUP BY Unit_sn
        HAVING COUNT(*) > 1;
        '''
    
    try:
        check_in_results = db.execute(check_in_query, (end_date, start_date)).fetchall()
        repeated_check_ins = [
            {
                "Unit_sn": row[0],
                "last_request_date": row[1],
                "check_count": row[2],
                "status": "In"
            } for row in check_in_results
        ]

        check_out_results = db.execute(check_out_query, (end_date, start_date)).fetchall()
        repeated_check_outs = [
            {
                "Unit_sn": row[0],
                "last_request_date": row[1],
                "check_count": row[2],
                "status": "Out"
            } for row in check_out_results
        ]

        repeated_requests = repeated_check_ins + repeated_check_outs

        return jsonify({'status': 'success', 'data': repeated_requests})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/add_part', methods=['POST'])
def add_part():
    data = request.get_json()
    print(data)
    result = insert_part(data)
    if result['status'] == 'success':
        return jsonify({'status': 'success', 'message': result['message']})
    else:
        return jsonify({'status': 'error', 'message': result['message']}), 400


@app.route('/sort_parts', methods=['POST'])
def sort_parts():
    """Sort parts based on a specified column and order, handling numeric values and units properly."""
    column = request.form.get('column')
    order = request.form.get('order', 'asc')  # Default to ascending if not specified
    search_term = request.form.get('search', '').lower()  # Get search term to allow for sorting
    parts = get_all_parts()  # Assume this function fetches all parts

    def extract_number(text):
        """Extracts the leading number from a string, converts it to float, and adjusts for unit."""
        number = 0
        match = re.search(r'(\d+)\s*(GB|TB)', text, re.IGNORECASE)
        if match:
            number = float(match.group(1))
            unit = match.group(2)
            if unit.upper() == 'TB':  # Convert terabytes to gigabytes
                number *= 1024
        return number

  # If items being searched for
    if search_term:
        def filter_parts(part):
            """Returns True if any of the part's attributes match the search term."""
            return (
                search_term in str(part['Type']).lower() or
                search_term in str(part['Capacity']).lower() or
                search_term in str(part['Size']).lower() or
                search_term in str(part['Speed']).lower() or
                search_term in str(part['Brand']).lower() or
                search_term in str(part['Model']).lower() or
                search_term in str(part['Location']).lower() or
                search_term in str(part['Part_sn']).lower()
            )

        filtered_parts = list(filter(filter_parts, parts))
    else:
        # Display all parts if no search term is provided
        filtered_parts = parts


    # Check if column is one of the acceptable fields to sort by
    if column in ['Type', 'Capacity', 'Size', 'Speed', 'Brand', 'Model', 'Location', 'Part_sn']:
        # Determine the sorting key and direction
        if column == 'Capacity':
            # Special handling for capacity to sort numerically and consider units
            sorted_parts = sorted(filtered_parts, key=lambda part: (part[column] is None, extract_number(part[column])), reverse=(order == 'desc'))
        else:
            # Default sorting for other columns
            sorted_parts = sorted(filtered_parts, key=lambda part: (part[column] is None, part[column]), reverse=(order == 'desc'))
    else:
        sorted_parts = filtered_parts  # Return unsorted if column is not valid

    return jsonify([dict(part) for part in sorted_parts])

import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/check_part_in_inventory', methods=['POST'])
def check_part_in_inventory():
    data = request.get_json()
    ### data object structure RC ###
    # action: "OUT"
    # note: ""
    # parts:
    #   0 {
    #      Capacity:    "4GB"
    #      Part_sn:     "00000001"
    #      Size:        null
    #      Speed:       null
    #      Type:        "PC3"
    #   }
    # technology: "Laptop"
    # tid: "TI000000-00000001"
    # unit_sn: "123456"
    ###

    # Extract the part serial numbers to look up in the database
    part_sn_list = [part['Part_sn'] for part in data['parts']]
    
    # Create the response JSON object structure
    # Only need to check these
    partsEdgeCases = {
        "mismatchSize": {"part": []},
        "mismatchType": {"part": []},
        "mismatchCapacity": {"part": []},
        "alreadyCheckedIn": {"part": []},
        "alreadyCheckedOut": {"part": []},
        "doesntExist": {"part": []}
    }

    # Connect to the database
    conn = get_db()
    try:
        # Fetch all parts from the database with matching Part_sn values
        # The use of placeholders (', '.join('?' for _ in part_sn_list))
        # helps in constructing the query dynamically to match the number
        # of parts provided.
        placeholders = ', '.join('?' for _ in part_sn_list)
        query = f'SELECT * FROM Part WHERE Part_sn IN ({placeholders})'
        db_parts = conn.execute(query, part_sn_list).fetchall()

        # Convert database results to a dictionary for easier lookup by Part_sn
        db_parts_dict = {dict(part)['Part_sn']: dict(part) for part in db_parts}
        
        # Iterate over each part from the data object and compare with the database values
        for part in data['parts']:
            part_sn = part['Part_sn']
            db_part = db_parts_dict.get(part_sn)

            if not db_part:
                # Part doesn't exist in the database
                partsEdgeCases["doesntExist"]["part"].append(part)
                continue

            # Check for mismatch in Size if Type is PC3, PC3L, or PC4
            if part['Type'] in ['PC3', 'PC3L', 'PC4'] and db_part['Size'] != part['Size']:
                updated_part = part.copy()
                updated_part['requestedSize'] = part['Size']
                updated_part['Size'] = db_part['Size']
                partsEdgeCases["mismatchSize"]["part"].append(updated_part)

            # Check for missing or mismatched attributes and update response with actual values
            if db_part['Type'] != part['Type']:
                updated_part = part.copy()
                updated_part['requestedType'] = part['Type']
                updated_part['Type'] = db_part['Type']
                partsEdgeCases["mismatchType"]["part"].append(updated_part)
                
            if db_part['Capacity'] != part['Capacity']:
                updated_part = part.copy()
                updated_part['requestedCapacity'] = part['Capacity']
                updated_part['Capacity'] = db_part['Capacity']
                partsEdgeCases["mismatchCapacity"]["part"].append(updated_part)

            # Check if the part is already checked in or out
            # data['Action'] comes from the homepage buttons and its UPPERCASE
            # db_part['Status'] is the current status and its Capitalized
            if data['action'] == 'IN' and db_part['Status'] == 'In':
                partsEdgeCases["alreadyCheckedIn"]["part"].append(part)
            elif data['action'] == 'OUT' and db_part['Status'] == 'Out':
                partsEdgeCases["alreadyCheckedOut"]["part"].append(part)

    finally:
        conn.close()

    # Return the response JSON object
    return jsonify(partsEdgeCases)


@app.route('/update_part_status', methods=['POST'])
def update_part_status():
    data = request.get_json()
    part_sn = data['Part_sn']
    tid = data['TID']
    unit_sn = data['Unit_sn']
    part_status = data['Part_status']  # update the part status given
    location = data.get('Location')
    note = data['Note']

    conn = get_db()
    try:
        conn.execute('BEGIN')
        # Update Part to set Status
        conn.execute('UPDATE Part SET Status = ?, Location = ? WHERE Part_sn = ?', (part_status, location, part_sn))
        # Insert a new log entry with the current timestamp, don't need location here (potentially)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time, Note) VALUES (?, ?, ?, ?, ?, ?)', 
                     (tid, unit_sn, part_sn, part_status, timestamp, note))
        
        # Fetch the part details
        part = conn.execute('SELECT * FROM Part WHERE Part_sn = ?', (part_sn,)).fetchone()

        conn.commit()
        return jsonify({
            'status': 'success',
            'data': {
                'timestamp': timestamp,
                'action': part_status,
                'TID': tid,
                'unit_sn': unit_sn,
                'Type': part['Type'],
                'Capacity': part['Capacity'],
                'Size': part['Size'],
                'Speed': part['Speed'],
                'Brand': part['Brand'],
                'Model': part['Model'],
                'Location': part['Location'],
                'Part_sn': part_sn
            }
        })
    except sqlite3.Error as e:
        # Roll back any changes if there was an error
        conn.rollback()
        return jsonify({'status': 'error', 'message': 'Database error: ' + str(e)}), 500

    finally:
        conn.close()


@app.route('/automated_test')
def automated_test():
    """
    This is a route to automatically perform SQL injection testing using the TID column of the Log table.
    This test includes values for all required fields to satisfy NOT NULL constraints. 

    """
    # Define a potentially malicious input simulating what a user might enter in a text area.
    malicious_input = "Valid Entry'; DROP TABLE Part; --"

    # Call the function that simulates handling of text area input
    try:
        
        response = simulate_text_area_input(malicious_input)
        return jsonify({'status': 'success', 'response': response}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def simulate_text_area_input(user_input):
    """
    Simulates the processing of text area input that constructs SQL queries using the TID column.
    Ensures that all non-nullable columns are given values to prevent NOT NULL constraint failures.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Simulated insertion into Log table with all necessary fields
        cursor.execute(
            "INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status) VALUES (?, ?, ?, ?)",
            (user_input, 'Unit123', 'Part123', 'In')  # Dummy values for Unit_sn, Part_sn, and Part_status
        )
        conn.commit()
        return "Simulated input was processed safely."
    except Exception as e:
        conn.rollback()
        return f"Failed to process simulated input: {str(e)}"
    finally:
        conn.close()


@app.route('/get_utilization', methods=['GET'])
def get_utilization():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    # Check for complete parameters
    if not month or not year:
        return jsonify({'status': 'error', 'message': 'Month and year are required.'}), 400

    # Set date range for query
    first_day = datetime(year, month, 1)
    last_day = datetime(year + (1 if month == 12 else 0), (month % 12) + 1, 1)

    db = get_db()
    query = '''
    SELECT 
        COUNT(CASE WHEN Part_status = 'In' THEN 1 END) AS checked_in,
        COUNT(CASE WHEN Part_status = 'Out' THEN 1 END) AS checked_out
    FROM Log
    WHERE Date_time >= ? AND Date_time < ?
    '''

    try:
        result = db.execute(query, (first_day, last_day)).fetchone()
        utilization_data = {
            'checked_in': result['checked_in'] or 0,
            'checked_out': result['checked_out'] or 0
        }

        return jsonify({'status': 'success', 'data': utilization_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/get_technology', methods=['GET'])
def get_technology():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    # Check for complete parameters
    if not month or not year:
        return jsonify({'status': 'error', 'message': 'Month and year are required.'}), 400

    # Set date range for query
    first_day = datetime(year, month, 1)
    last_day = datetime(year + (1 if month == 12 else 0), (month % 12) + 1, 1)

    db = get_db()
    query = '''
    SELECT 
        p.Type AS Technology, 
        COUNT(*) AS count
    FROM Log l
    JOIN Part p ON l.Part_sn = p.Part_sn
    WHERE l.Date_time >= ? AND l.Date_time < ?
    GROUP BY p.Type
    HAVING count > 0
    '''

    try:
        results = db.execute(query, (first_day, last_day)).fetchall()
        technology_data = {row['Technology']: row['count'] for row in results}

        return jsonify({'status': 'success', 'data': technology_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(port=8000)
    #app.run(debug=True)