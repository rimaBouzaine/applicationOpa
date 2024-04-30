import subprocess
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from gevent.pywsgi import WSGIServer
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import secrets

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'mysql-service'
app.config['MYSQL_USER'] = 'mysql'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'sample'

# Secret key for JWT
app.config['SECRET_KEY'] = secrets.token_hex(16)  

mysql = MySQL(app)

# Function to hash the password
def hash_password(password):
    return generate_password_hash(password)

# Route to add data to the database
@app.route('/data', methods=['POST'])
def add_data():
    # Extract data from request
    name = request.json.get('name')
    age = request.json.get('age')
    email = request.json.get('email')
    password = request.json.get('password')

    # Check if all required fields are present
    if not (name and age and email and password):
        return jsonify({'message': 'Incomplete data provided'}), 400

    # Hash the password
    hashed_password = hash_password(password)

    try:
        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO user (name, age, email, password) VALUES (%s, %s, %s, %s)''', (name, age, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data added successfully'})
    except Exception as e:
        return jsonify({'message': 'Error adding data', 'error': str(e)}), 500

# Route for user login
@app.route('/login', methods=['GET'])
def login():
    try:
        # Execute kubectl command to get service information
        result = subprocess.run(['kubectl', 'get', 'svc'], capture_output=True, text=True)
#        result = subprocess.run(['kubectl', 'get', 'svc','-n','gatekeeper-system'], capture_output=True, text=True)

        # Get username and password from request parameters
        username = request.args.get('username')
        password = request.args.get('password')

        # Check if username or password is missing
        if not (username and password):
            return jsonify({'message': 'Authentication required'}), 401

        # Query user from the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE name = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # Check if kubectl command executed successfully
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500

        # Check if user exists and password is correct
        if user and check_password_hash(user[4], password):
            # Generate JWT token
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    # Run the application using gevent WSGI server
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

