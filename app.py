from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import db_blueprint, get_db, get_all_parts, insert_part # checkout_part, checkin_part

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

@app.route('/add_part', methods=['POST'])
def add_part():
    try:
        print("add part 2")
        data = request.json
        print(data)
        insert_part(data['Type'], data['Capacity'], data['Size'], data['Speed'],
                    data['Brand'], data['Model'], data['Location'], data['Part_sn'])
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    expected_type = data['Type']
    expected_capacity = data['Capacity']

    conn = get_db()
    try:
        # Query to check if Part_sn exists in the Part table
        part = conn.execute('SELECT Type, Capacity FROM Part WHERE Part_sn = ?', (part_sn,)).fetchone()

        if part is None:
            return jsonify({'exists': False, 'error': 'not_in_inventory', 'message': 'Part not found in inventory.'})

        # Check if the existing part matches the expected type and capacity
        if part['Type'] != expected_type or part['Capacity'] != expected_capacity:
            return jsonify({
                'exists': False,
                'error': 'mismatch',
                'message': 'Mismatch in type or capacity.',
                'expected': {'Type': expected_type, 'Capacity': expected_capacity},
                'actual': {'Type': part['Type'], 'Capacity': part['Capacity']}
            })
        return jsonify({'exists': True, 'message': 'Part exists with matching type and capacity.'})

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


if __name__ == '__main__':
    # app.run(port=8000)
    app.run(debug=True)
