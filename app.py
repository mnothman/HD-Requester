from flask import Blueprint, current_app, Flask, g, jsonify, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import re, sqlite3

app = Flask(__name__)

app.secret_key = 'key'

# Test login
USERNAME = 'admin'
PASSWORD = 'admin123'

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
    return render_template('index.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate login credentials
        if username == USERNAME and password == PASSWORD:
            # If login is successful, redirect to the admin dashboard
            return redirect(url_for('admin_dashboard'))
        else:
             # If login fails, flash a message and render login again
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))  # Redirect back to login page
        

    # If GET request, render login page
    return render_template('adminLogin.html')

# Dashboard route
@app.route('/dashboard')
def admin_dashboard():
    parts = record()
    return render_template('dashboard.html', parts=parts)

def record():
    db = get_db()
    query = '''
SELECT l.Date_time, 
           CASE 
               WHEN l.Part_status = 'in' THEN 'Check In' 
               WHEN l.Part_status = 'out' THEN 'Check Out' 
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
           l.Part_sn
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

    # Update the Admin table with the new password in plain text
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Update the password in the Admin table (assuming only one admin user)
        cursor.execute("UPDATE Admin SET password = ? WHERE username = ?", (new_password, 'admin'))  # Replace 0 with actual Admin ID if necessary
        conn.commit()

        return jsonify({'success': True, 'message': 'Password has been updated successfully.'})
    except sqlite3.Error as e:
        # If an error occurs, rollback the transaction and send an error message
        conn.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while updating the password: ' + str(e)})
    finally:
        conn.close()




@app.route('/get_parts', methods=['POST'])
def get_parts(): #fetch parts from search
    search_type = request.form.get('searchType', None)
    parts = get_all_parts(search_type)
    return jsonify([dict(part) for part in parts])

def get_all_parts(search_type=None):
    db = get_db()
    query = 'SELECT Part.* FROM Part JOIN Part_log ON Part.Part_sn = Part_log.Part_sn WHERE Part_log.Part_status IS "in"'
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
        JOIN
            Part_log pl ON p.Part_sn = pl.Part_sn
        WHERE
            pl.Part_status = 'in'
        GROUP BY
            p.Type,
            p.Size
        ORDER BY
            p.Type,
            p.Size;
    '''
    try:
        # Execute the query and fetch all results
        result = db.execute(query).fetchall()
        return result
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {str(e)}")

@app.route('/get_unique_parts', methods=['GET'])
def get_unique_parts():
    db = get_db()
    query = 'SELECT DISTINCT Type FROM Part ORDER BY Type'
    try:
        result = db.execute(query).fetchall()
        names = [row['Type'] for row in result]
        return jsonify(names)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_part_capacities', methods=['GET'])
def get_part_capacities():
    name = request.args.get('name')
    db = get_db()
    query = '''
        SELECT DISTINCT Capacity FROM Part
        WHERE Type = ?
    '''
    try:
        result = db.execute(query, (name,)).fetchall()
        capacities = [row['Capacity'] for row in result]
        return jsonify(capacities)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/inventory')
def inventory():
    return render_template('temp_inventory.html')

# Database function to insert a part
def insert_part(part_data):
    # Connection to your SQLite database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # SQL query to insert a new part into the Part table
        conn.execute('BEGIN')
        cursor.execute('''
            INSERT INTO Part (Type, Capacity, Size, Speed, Brand, Model, Location, Part_sn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (part_data['Type'], part_data['Capacity'], part_data['Size'], part_data['Speed'],
              part_data['Brand'], part_data['Model'], part_data['Location'], part_data['Part_sn']))

        # SQL query to insert a new record into the Part_log table
        cursor.execute('''
            INSERT INTO Part_log (Part_sn, Part_status)
            VALUES (?, 'in')
        ''', (part_data['Part_sn'],))

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

    return {'status': 'success', 'message': 'Part added successfully and logged as in'}


@app.route('/add_part', methods=['POST'])
def add_part():
    data = request.get_json()
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


@app.route('/check_part_in_inventory', methods=['POST'])
def check_part_in_inventory():
    data = request.get_json()
    part_sn = data['Part_sn']
    size = data['Size']
    expected_type = data['Type']
    expected_capacity = data['Capacity']
    expected_part_status = data['Part_status']

    conn = get_db()
    try:
        # Query to check if Part_sn exists in the Part table and is currently checked out
        part = conn.execute('SELECT * FROM Part_log pl JOIN Part p on pl.Part_sn = p.Part_sn WHERE p.Part_sn = ?', (part_sn,)).fetchone()

        if part is None:
            return jsonify({'exists': False,
							'error': 'not_in_inventory',
							'message': 'Part not found in inventory.',
						   })

        # Check if the existing part matches the expected type and capacity
        elif part['Type'] != expected_type or part['Capacity'] != expected_capacity:
            return jsonify({
                'exists': False,
                'error': 'mismatch',
                'message': 'Mismatch in type or capacity.',
                'expected': {'Type': expected_type, 'Capacity': expected_capacity},
                'actual': {'Type': part['Type'], 'Capacity': part['Capacity']}
            })
		# Check if the existing part is already checked in
        elif part['Part_status'] == 'in':
            if expected_part_status == 'in':
                return jsonify({
                    'exists': False,
                    'error': 'checked-in',
                    'message': 'Already checked-in.',
                    'part': {'Part_sn': part_sn,
                             'Type': part['Type'],
                             'Capacity': part['Capacity'],
                             'Size': part['Size'],
                             'Speed': part['Speed'],
                             'Brand': part['Brand'],
                             'Model': part['Model'],
                             'Location': part['Location']}
                })
            else:
                return jsonify({'exists': True, 'message': 'Part exists with matching type and capacity.'})
        # Check if the existing part is already checked out
        elif part['Part_status'] == 'out':
            if expected_part_status == 'out':
                return jsonify({
                    'exists': False,
                    'error': 'checked-out',
                    'message': 'Already checked-out.',
                    'part': {'Part_sn': part_sn,
                             'Type': part['Type'],
                             'Capacity': part['Capacity'],
                             'Size': part['Size'],
                             'Speed': part['Speed'],
                             'Brand': part['Brand'],
                             'Model': part['Model'],
                             'Location': part['Location']}
                })
            else:
                return jsonify({'exists': True, 'message': 'Part exists with matching type and capacity.'})
        else:
            return jsonify({
                'exists': False,
                'error': 'uncaught',
                'message': 'Uncaught error.',
                'part': {'Part_sn': part_sn, 'Type': part['Type'], 'Capacity': part['Capacity'], 'Size': part['Size']}
            })

    finally:
        conn.close()


@app.route('/update_part_status', methods=['POST'])
def update_part_status():
    data = request.get_json()
    part_sn = data['Part_sn']
    tid = data['TID']
    unit_sn = data['Unit_sn']
    part_status = data['Part_status']  # update the part status given

    conn = get_db()
    try:
        conn.execute('BEGIN')
        # Update Part_log to set Part_status to 'in'
        conn.execute('UPDATE Part_log SET Part_status = ? WHERE Part_sn = ?', (part_status, part_sn))
        # Insert a new log entry with the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time) VALUES (?, ?, ?, ?, ?)', 
                     (tid, unit_sn, part_sn, part_status, timestamp))
#        conn.commit()
 #       return jsonify({'status': 'success', 'message': 'Part status updated and logged successfully.'})

           # Fetch the part details
        part = conn.execute('SELECT * FROM Part WHERE Part_sn = ?', (part_sn,)).fetchone()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
                'Part_sn': part_sn
            }
        })
    except sqlite3.Error as e:
        # Roll back any changes if there was an error
        conn.rollback()
        return jsonify({'status': 'error', 'message': 'Database error: ' + str(e)}), 500

    finally:
        conn.close()


@app.route('/reset_log_tables', methods=['POST'])
def reset_log_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Dropping tables
        cursor.execute("DROP TABLE IF EXISTS Log;")
        cursor.execute("DROP TABLE IF EXISTS Part_log;")
        
        # Recreating tables
        cursor.execute('''
            CREATE TABLE "Part_log" (
                "Part_sn" TEXT NOT NULL UNIQUE,
                "Part_status" TEXT NOT NULL CHECK("Part_status" IN ('in', 'out', 'deleted')),
                FOREIGN KEY("Part_sn") REFERENCES "Part"("Part_sn")
            );
        ''')
        cursor.execute('''
            CREATE TABLE "Log" (
                "TID" TEXT NOT NULL,
                "Unit_sn" TEXT NOT NULL,
                "Part_sn" TEXT NOT NULL,
                "Part_status" TEXT NOT NULL,
                "Date_time" TEXT,
                CONSTRAINT "fk_l_status" FOREIGN KEY("Part_status") REFERENCES "Part_log"("Part_status"),
                CONSTRAINT "fk_l_unitsn" FOREIGN KEY("Unit_sn") REFERENCES "Part_log"("Unit_sn"),
                CONSTRAINT "fk_l_partsn" FOREIGN KEY("Part_sn") REFERENCES "Part_log"("Part_sn"),
                CONSTRAINT "pk_l_datetime_tid" PRIMARY KEY("Date_time","TID")
            );
        ''')

        # Inserting initial data into Part_log
        parts_data = [
            ('00000001', 'in'), ('00000002', 'in'), ('00000003', 'in'),
            ('00000004', 'in'), ('00000005', 'in'), ('00000006', 'in'),
            ('00000007', 'in'), ('00000008', 'in'), ('00000009', 'in'),
            ('00000010', 'in'), ('00000022', 'out')
        ]
        cursor.executemany('INSERT INTO Part_log (Part_sn, Part_status) VALUES (?, ?);', parts_data)

        conn.commit()  # Commit the changes
        return jsonify({'status': 'success', 'message': 'Database has been reset successfully.'})
    except sqlite3.Error as e:
        conn.rollback()  # Roll back any changes if something goes wrong
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        conn.close()

@app.route('/automated_test')
def automated_test():
    """
    A route to automatically perform SQL injection testing using the TID column of the Log table.
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
            (user_input, 'Unit123', 'Part123', 'in')  # Dummy values for Unit_sn, Part_sn, and Part_status
        )
        conn.commit()
        return "Simulated input was processed safely."
    except Exception as e:
        conn.rollback()
        return f"Failed to process simulated input: {str(e)}"
    finally:
        conn.close()



if __name__ == '__main__':
    # app.run(port=8000)
    app.run(debug=True)

#test blank line
