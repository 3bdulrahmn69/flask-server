from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import random
import string
import re
import logging

# Create the Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='server.log', level=logging.INFO)

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('licenses.db')
    cursor = conn.cursor()
    # Create table for license keys
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        exp_date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Function to generate a random license key
def generate_license_key():
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=4))
    key = f"{letters}-{digits}-{letters}-{digits}"
    return key

# Function to check if a license key already exists in the database
def license_key_exists(license_key):
    conn = sqlite3.connect('licenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM licenses WHERE key = ?', (license_key,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Function to add a new license key to the database
def add_license_key(name, exp_date):
    try:
        exp_date_db_format = datetime.strptime(exp_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        license_key = generate_license_key()
        while license_key_exists(license_key):
            license_key = generate_license_key()

        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO licenses (key, name, exp_date) VALUES (?, ?, ?)', 
                        (license_key, name, exp_date_db_format))
        conn.commit()
        return license_key
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error occurred while adding license key: {e}")
        return None
    finally:
        conn.close()

# Function to check license key in the database
def check_license_key(license_key):
    try:
        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('SELECT exp_date FROM licenses WHERE key = ?', (license_key,))
        result = cursor.fetchone()
        if result:
            exp_date = datetime.strptime(result[0], '%Y-%m-%d')
            if exp_date >= datetime.now():
                return {'status': True, 'message': 'valid key'}
            else:
                return {'status': False, 'message': 'expired key'}
        else:
            return None
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error occurred while checking license key: {e}")
        return None
    finally:
        conn.close()

# Function to delete a license key from the database
def delete_license_key(license_key):
    try:
        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM licenses WHERE key = ?', (license_key,))
        conn.commit()
        rows_deleted = cursor.rowcount
        return rows_deleted > 0
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error occurred while deleting license key: {e}")
        return False
    finally:
        conn.close()

# Updated API endpoint to check the license key using POST and request body
@app.route('/check-license', methods=['POST'])
def check_license():
    data = request.get_json()
    license_key = data.get('key')

    if not license_key:
        return jsonify({'message': 'No key provided'}), 400

    # Validate the license key format
    if not re.match(r'^[A-Z]{4}-\d{4}-[A-Z]{4}-\d{4}$', license_key):
        return jsonify({'message': 'Invalid key format. Expected format: AAAA-1111-BBBB-2222'}), 400

    # Check the license key
    result = check_license_key(license_key)

    if result is None:
        return jsonify({'message': 'Key Not Found'}), 404
    elif result['status']:
        return jsonify({'isKeyWork': True, 'message': result['message']}), 200
    else:
        return jsonify({'isKeyWork': False, 'message': result['message']}), 200

# API endpoint to add a new license key
@app.route('/add-license', methods=['POST'])
def add_license():
    data = request.get_json()
    name = data.get('name')
    exp_date = data.get('exp_date')

    if not name or not exp_date:
        return jsonify({'message': 'Name or expiration date not provided'}), 400

    # Add the license key
    license_key = add_license_key(name, exp_date)

    if license_key is None:
        return jsonify({'message': 'Failed to add license key, key might already exist'}), 500

    return jsonify({'key': license_key, 'message': 'License key added successfully'}), 201

# API endpoint to delete a license key
@app.route('/delete-license', methods=['DELETE'])
def delete_license():
    data = request.get_json()
    license_key = data.get('key')

    if not license_key:
        return jsonify({'message': 'No key provided'}), 400

    # Delete the license key
    if delete_license_key(license_key):
        return jsonify({'message': 'License key deleted successfully'}), 200
    else:
        return jsonify({'message': 'Key Not Found'}), 404

if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)
