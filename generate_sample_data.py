import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('refresh.db')
cursor = conn.cursor()

# Function to generate random part data
def generate_part_data(part_sn):
    types = ['PC3', 'PC3L', 'PC4', 'HD 3.5', 'HD 2.5', 'SSD', 'm.2', 'NVMe', 'mSATA', 'Apple']
    capacities = ['128GB', '256GB', '512GB', '1TB', '2TB', '4TB']
    sizes = ['2.5"', '3.5"', 'Laptop', 'Desktop']
    speeds = ['1600MHz', '1866MHz', '2400MHz', '3200MHz', '3600MHz']
    brands = ['Kingston', 'Samsung', 'WD', 'Seagate', 'Crucial', 'Corsair', 'Apple']
    models = ['Model A', 'Model B', 'Model C', 'Model D', 'Model E']
    locations = [f'Shelf {i} C{random.randint(1, 10)}' for i in range(1, 11)] + [f'Box {i} C{random.randint(1, 10)}' for i in range(1, 11)]

    part_type = random.choice(types)
    capacity = random.choice(capacities)
    size = random.choice(sizes)
    speed = random.choice(speeds)
    brand = random.choice(brands)
    model = random.choice(models)
    location = random.choice(locations)

    return (part_type, capacity, size, speed, brand, model, location, part_sn)

# Insert sample parts
for i in range(1, 5001):
    part_sn = f'{i:08d}'  # Sequential serial number
    part_data = generate_part_data(part_sn)
    cursor.execute('INSERT INTO Part (Type, Capacity, Size, Speed, Brand, Model, Location, Part_sn) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', part_data)

# Function to generate random log entry
def generate_log_entry(part_sn):
    actions = ['in', 'out', 'deleted']
    action = random.choice(actions)
    tid = f'TI-{random.randint(10000000, 99999999)}'
    unit_sn = f'UN-{random.randint(10000, 99999)}'
    date_time = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')

    return (part_sn, action, tid, unit_sn, date_time)

# Insert sample part log entries
for i in range(1, 5001):
    part_sn = f'{i:08d}'
    log_entry = generate_log_entry(part_sn)
    cursor.execute('INSERT INTO Part_log (Part_sn, Part_status) VALUES (?, ?)', (log_entry[0], log_entry[1]))
    cursor.execute('INSERT INTO Log (TID, Unit_sn, Part_sn, Part_status, Date_time) VALUES (?, ?, ?, ?, ?)', log_entry)

# Commit and close
conn.commit()
conn.close()

print("Sample data has been generated successfully!")
