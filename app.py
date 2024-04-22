from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import sqlite3, db_blueprint, get_db, get_all_parts # checkout_part, checkin_part

app = Flask(__name__)
app.register_blueprint(db_blueprint)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_parts', methods=['POST'])
def get_parts(): #fetch parts from search
    print("gets parts here 2")
    search_type = request.form.get('searchType', None)
    parts = get_all_parts(search_type)
    return jsonify([dict(part) for part in parts])

# Sample database function to insert a part
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
    try:
        insert_part(data)  # Assuming data is a dictionary matching your database schema
        return jsonify({'status': 'success', 'message': 'Part added successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/sort_parts', methods=['POST'])
def sort_parts():
    """Sort parts based on a specified column."""
    column = request.form.get('column')
    parts = get_all_parts()  #all parts to sort
    # validate first
    if column in ['Type', 'Capacity', 'Size', 'Speed', 'Brand', 'Model', 'Location', 'Part_sn']:
        sorted_parts = sorted(parts, key=lambda part: (part[column] is None, part[column]))
    else:
        sorted_parts = parts
    return jsonify([dict(part) for part in sorted_parts])

@app.route('/check_part_in_inventory', methods=['POST'])
def check_part_in_inventory():
    data = request.get_json()
    part_sn = data['Part_sn']
    size = data['Size']
    expected_type = data['Type']
    expected_capacity = data['Capacity']

    conn = get_db()
    try:
        # Query to check if Part_sn exists in the Part table and is currently checked out
        part = conn.execute('SELECT Type, Capacity, Size, Part_status FROM Part_log pl JOIN Part p on pl.Part_sn = p.Part_sn WHERE p.Part_sn = ?', (part_sn,)).fetchone()

        if part is None:
            return jsonify({'exists': False,
							'error': 'not_in_inventory',
							'message': 'Part not found in inventory.',
						   })

        # Check if the existing part matches the expected type and capacity
        if part['Type'] != expected_type or part['Capacity'] != expected_capacity:
            return jsonify({
                'exists': False,
                'error': 'mismatch',
                'message': 'Mismatch in type or capacity.',
                'expected': {'Type': expected_type, 'Capacity': expected_capacity},
                'actual': {'Type': part['Type'], 'Capacity': part['Capacity']}
            })
		# Check if the existing part is already checked in
        if part['Part_status'] != 'in':
            return jsonify({'exists': True, 'message': 'Part exists with matching type and capacity.'})
        else:
            return jsonify({
                'exists': False,
                'error': 'checked-in',
                'message': 'Already checked-in.',
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
    part_status = 'in'  # We are checking in the part, so we set this status to 'in'

    conn = get_db()
    try:
        conn.execute('BEGIN')
        # Update Part_log to set Part_status to 'in'
        conn.execute('UPDATE Part_log SET Part_status = ? WHERE Part_sn = ?', (part_status, part_sn))
        conn.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status) VALUES (?, ?, ?, ?)', 
                     (tid, unit_sn, part_sn, part_status))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Part status updated and logged successfully.'})

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

if __name__ == '__main__':
    # app.run(port=8000)
    app.run(debug=True)
