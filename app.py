from flask import Flask, render_template, request, redirect, session
from database import db_blueprint, get_all_parts, checkout_part, checkin_part
from flask import request, redirect, url_for

app = Flask(__name__)
app.register_blueprint(db_blueprint)
app.secret_key = 'your_secret_key'

#Temporary User Dictionary
USER_CREDENTIALS = {
    'admin': 'password',
    'user1': '123456'
}

#Authenticates User Creds
def authenticate_user(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        return True
    return False

#The Routes
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', message = 'Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def pc_parts():
    parts = get_all_parts()
    return render_template('search_results.html', parts=parts)

@app.route('/search')
def search():
    search_type = request.args.get('type', '')
    parts = get_all_parts(search_type)
    return render_template('search_results.html', parts=parts, search_type=search_type)

@app.route('/checkout', methods=['POST'])
def checkout():
    serial_number = request.form['serial_number']
    checkout_part(serial_number)  
    return redirect(url_for('pc_parts')) #need to change this for it to go to out panel instead of out it by itself

@app.route('/checkin', methods=['POST'])
def checkin():
    serial_number = request.form['serial_number']
    part_type = request.form['part_type']
    brand = request.form['brand']
    shelf_location = request.form['shelf_location']
    checked_out = request.form['checked_out']
    checkin_part(serial_number, part_type, brand, shelf_location, checked_out)
    return redirect(url_for('pc_parts'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
