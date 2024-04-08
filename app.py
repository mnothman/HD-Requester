from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import db_blueprint, get_all_parts, insert_part # checkout_part, checkin_part

app = Flask(__name__)
app.register_blueprint(db_blueprint)
app.secret_key = 'your_secret_key'  # use env variable for production

USER_CREDENTIALS = {'admin': 'password', 'user1': '123456'}

def authenticate_user(username, password):
    return USER_CREDENTIALS.get(username) == password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_parts', methods=['POST'])
def get_parts(): #fetch parts from search
    search_type = request.form.get('searchType', None)
    parts = get_all_parts(search_type)
    return jsonify([dict(part) for part in parts])

@app.route('/add_part', methods=['POST'])
def add_part():
    try:
        data = request.form
        insert_part(data['Type'], data['Capacity'], data['Size'], data['Speed'],
                    data['Brand'], data['Model'], data['Location'], data['Part_sn'])
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        if authenticate_user(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect('/dashboard')
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard with all parts or filtered by type."""
    search_type = request.args.get('type', '')
    parts = get_all_parts(search_type)
    return render_template('search_results.html', parts=parts, search_type=search_type)

@app.route('/checkout', methods=['POST'])
def checkout():
    """Mark a part as checked out."""
    serial_number = request.form['serial_number']
    # checkout_part(serial_number)  # implement later
    return redirect(url_for('dashboard'))

@app.route('/checkin', methods=['POST'])
def checkin():
    serial_number = request.form['serial_number']
    # add aditional fields to checkin

    # checkin_part(serial_number)  # implement later
    return redirect(url_for('dashboard'))

@app.route('/sort_parts', methods=['POST'])
def sort_parts():
    """Sort parts based on a specified column."""
    column = request.form.get('column')
    parts = get_all_parts()  #all parts to sort
    # validate first
    if column in ['Type', 'Capacity', 'Size', 'Speed', 'Brand', 'Model', 'Location', 'Part_sn']:
        sorted_parts = sorted(parts, key=lambda part: part[column] if column in part else '')
    else:
        sorted_parts = parts
    return jsonify([dict(part) for part in sorted_parts])

@app.route('/logout')
def logout():
    #log out current user
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
