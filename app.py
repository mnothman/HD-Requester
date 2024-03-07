from flask import Flask, render_template
from database import db_blueprint, get_all_parts, checkout_part
from flask import request, redirect, url_for

app = Flask(__name__)
app.register_blueprint(db_blueprint)

@app.route('/')
def pc_parts():
    parts = get_all_parts()
    return render_template('pc_parts.html', parts=parts)

@app.route('/search')
def search():
    search_type = request.args.get('type', '')
    parts = get_all_parts(search_type)
    return render_template('search_results.html', parts=parts, search_type=search_type)

@app.route('/checkout', methods=['POST'])
def checkout():
    serial_number = request.form['serial_number']
    checkout_part(serial_number)  
    return redirect(url_for('parts')) 

if __name__ == '__main__':
    app.run(debug=True)
