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

    current_app.logger.info("Database is connected")

def get_all_parts(search_type=None):
    db = get_db()
    query = 'SELECT Part.* FROM Part JOIN Part_log ON Part.Part_sn = Part_log.Part_sn WHERE Part_log.Part_status IS "in"'
    args = ()
    if search_type:
        query += ' AND Type LIKE ?'
        args = ('%' + search_type + '%',)
    parts = db.execute(query, args).fetchall()
    return parts


# commented out for now
"""
def checkout_part(serial_number): #need to change these buttons to not submit
    db = get_db()
    db.execute('UPDATE parts SET checked_out = 1 WHERE serial_number = ?', (serial_number,))
    db.commit()


def checkin_part(serial_number, part_type, brand, shelf_location, checked_out): #checked_out needs to stay here
    db = get_db()
    db.execute('INSERT INTO parts (serial_number, part_type, brand, shelf_location, checked_out) VALUES (?, ?, ?, ?, 0)',  #comes as 0 for checked_out
               (serial_number, part_type, brand, shelf_location))
    db.commit()
"""