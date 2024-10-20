import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('refresh.db')
cursor = conn.cursor()

def drop_and_create_tables():
    query = '''
    drop table Log;
    drop table Part;

    CREATE TABLE "Log" (
	"TID"	TEXT NOT NULL,
	"Unit_sn"	TEXT NOT NULL,
	"Part_sn"	TEXT NOT NULL,
	"Part_status"	TEXT NOT NULL,
	"Date_time"	DATETIME,
	"Note"	TEXT,
	FOREIGN KEY("Part_sn") REFERENCES "Part"("Part_sn"),
	PRIMARY KEY("Date_time","Part_sn")
    );

    CREATE TABLE "Part" (
	"Part_sn"	TEXT,
	"Type"	TEXT NOT NULL,
	"Capacity"	TEXT NOT NULL,
	"Size"	TEXT,
	"Speed"	NUMERIC,
	"Brand"	TEXT NOT NULL,
	"Model"	TEXT NOT NULL,
	"Location"	TEXT,
	"Status"	TEXT NOT NULL CHECK("Status" IN ('In', 'Out', 'Deleted')),
	"Timedate_updated"	DATETIME,
	PRIMARY KEY("Part_sn")
    );

    UPDATE Part
    SET
        Type = 'PC4',
        Capacity = '4GB',
        Size = 'Laptop',
        Speed = '2400T',
        Brand = 'SK Hynix'
    WHERE
        Part_sn = '00000001';

    '''
    cursor.executescript(query)
    conn.commit()


# Update the Part with Serial number=00000001 for our Tests to work
def update_first_part_record():
    query = '''
    UPDATE Part
    SET
        Type = 'PC4',
        Capacity = '4GB',
        Size = 'Laptop',
        Speed = '2400T',
        Brand = 'SK Hynix'
    WHERE
        Part_sn = '00000001';
    '''
    cursor.execute(query)
    conn.commit()


# Function to generate random part data
def generate_part_data(part_sn):
    types = ['PC3', 'PC3L', 'PC4', 'HD', 'SSD', 'm.2', 'NVMe', 'mSATA', 'Apple']
    capacities = {
        'PC3': ['2GB', '4GB', '8GB'],
        'PC3L': ['2GB', '4GB', '8GB'],
        'PC4': ['2GB', '4GB', '8GB', '16GB', '32GB', '64GB', '128GB'],
        'HD': ['300GB', '500GB', '600GB', '750GB', '1TB', '1.5TB', '2TB', '3TB', '4TB', '5TB'],
        'SSD': ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB'],
        'm.2': ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB'],
        'NVMe': ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB'],
        'mSATA': ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB'],
        'Apple': ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB']
    }
    
    sizes = {
        'PC3': ['Laptop', 'Desktop'],
        'PC3L': ['Laptop', 'Desktop'],
        'PC4': ['Laptop', 'Desktop'],
        'HD': ['2.5"', '3.5"'],
        'SSD': [None],
        'm.2': [None],
        'NVMe': [None],
        'mSATA': [None],
        'Apple': [None]
    }
    
    speeds = {
        'PC3': ['8500R', '8500U', '8500U', '10600U', '12800U', '10600U', '12800U', '8500E'],
        'PC3L': ['10600U', '12800U'],
        'PC4': ['2133P', '2400P', '2400T', '2666V', '3200AA'],
        'HD': [None],
        'SSD': [None],
        'm.2': [None],
        'NVMe': [None],
        'mSATA': [None],
        'Apple': [None]
    }
    
    brands = ['Kingston', 'Samsung', 'WD', 'Seagate', 'Crucial', 'Corsair', 'Apple']
    models = ['Model A', 'Model B', 'Model C', 'Model D', 'Model E']
    locations = [f'Shelf {i} C{random.randint(1, 10)}' for i in range(1, 11)] + [f'Box {i} C{random.randint(1, 10)}' for i in range(1, 11)]
    
    # Generate random date for timedate_updated (between 2019-01-01 and 2024-10-15)
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2024, 10, 15)
    random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

    part_type = random.choice(types)
    capacity = random.choice(capacities[part_type])
    size = random.choice(sizes[part_type])
    speed = random.choice(speeds[part_type])
    brand = 'Apple' if part_type == 'Apple' else random.choice([b for b in brands if b != 'Apple' or part_type == 'Apple'])
    model = random.choice(models)
    location = random.choice(locations)
    status = 'In'

    return (part_sn, part_type, capacity, size, speed, brand, model, location, status, random_date)


drop_and_create_tables()

# Insert sample parts
for i in range(1, 5001):
    part_sn = f'{i:08d}'  # Sequential serial number
    part_data = generate_part_data(part_sn)
    cursor.execute('INSERT INTO Part (Part_sn, Type, Capacity, Size, Speed, Brand, Model, Location, Status, timedate_updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', part_data)

# Function to generate random log entry
def generate_log_entry(part_sn):
    actions = ['In', 'Out', 'Deleted']
    action = random.choice(actions)
    tid = f'TI-{random.randint(10000000, 99999999)}'
    unit_sn = f'UN-{random.randint(10000, 99999)}'
    date_time = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')
    note = random.choice([''] * 9 + ['Gave the wrong part to Tech', 'Sales made a mistake', 'Tech made a mistake'] * 1)

    return (tid, unit_sn, part_sn, action, date_time, note)

# Insert sample part log entries
for i in range(1, 5001):
    part_sn = f'{i:08d}'
    log_entry = generate_log_entry(part_sn)
    cursor.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time, Note) VALUES (?, ?, ?, ?, ?, ?)', log_entry)

update_first_part_record()

# Commit and close
conn.commit()
conn.close()

print("Sample data has been generated successfully!")
