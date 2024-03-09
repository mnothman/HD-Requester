from flask import Blueprint, current_app, g
import sqlite3

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

def get_all_parts(search_type=None):
    db = get_db()
    query = 'SELECT * FROM parts'
    args = ()
    if search_type:
        query += ' WHERE part_type LIKE ?'
        args = ('%' + search_type + '%',)
    parts = db.execute(query, args).fetchall()
    return parts

def checkout_part(serial_number):
    db = get_db()
    db.execute('UPDATE parts SET checked_out = 1 WHERE serial_number = ?', (serial_number,))
    db.commit()


def checkin_part(serial_number, part_type, brand, shelf_location, checked_out): #checked_out needs to stay here
    db = get_db()
    db.execute('INSERT INTO parts (serial_number, part_type, brand, shelf_location, checked_out) VALUES (?, ?, ?, ?, 0)',  #comes as 0 for checked_out
               (serial_number, part_type, brand, shelf_location))
    db.commit()
