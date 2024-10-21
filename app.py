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


@app.route('/check_part_in_inventory', methods=['POST'])
def check_part_in_inventory():
    data = request.get_json()
    part_sn = data['Part_sn']
    size = data['Size']
    textarea_type = data['Type']
    textarea_capacity = data['Capacity']
    textarea_part_status = data['Part_status']

    conn = get_db()
    try:
        # Query to check if Part_sn exists in the Part table and is currently checked out
        part = conn.execute('SELECT * FROM Part WHERE Part_sn = ?', (part_sn,)).fetchone()

        if part is None:
            return jsonify({'exists': False,
							'error': 'not_in_inventory',
							'message': 'Part not found in inventory.',
						   })

        # Check if the existing part matches the textarea's type and capacity
        elif part['Type'] != textarea_type or part['Capacity'] != textarea_capacity:
            return jsonify({
                'exists': False,
                'error': 'mismatch',
                'message': 'Mismatch in type or capacity.',
                'expected': {'Type': textarea_type, 'Capacity': textarea_capacity},
                'actual': {'Type': part['Type'], 'Capacity': part['Capacity']}
            })
		# Check if the existing part is already checked in
        elif textarea_part_status == 'In':
            if part['Status'] == 'In':
                return jsonify({
                    'exists': False,    # make index.js around line 724 show the modal with this data 
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
        elif textarea_part_status == 'Out':
            if part['Status'] == 'Out':
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
                return jsonify({'exists': True,
                                'part': {'Part_sn': part_sn,
                                'Type': part['Type'],
                                'Capacity': part['Capacity'],
                                'Size': part['Size'],
                                'Speed': part['Speed'],
                                'Brand': part['Brand'],
                                'Model': part['Model'],
                                'Location': part['Location']},
                                'message': 'Part exists with matching type and capacity.'})
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
    note = data['Note']

    conn = get_db()
    try:
        conn.execute('BEGIN')
        # Update Part to set Status
        conn.execute('UPDATE Part SET Status = ? WHERE Part_sn = ?', (part_status, part_sn))
        # Insert a new log entry with the current timestamp
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




if __name__ == '__main__':
    # app.run(port=8000)
    app.run(debug=True)