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


if __name__ == '__main__':
    app.run(debug=True)
