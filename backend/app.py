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
@app.route('/login', methods=['POST'])
def login():
    try:
        # Get the JSON data from the request
        data = request.json

        # Check if login and password are provided in the JSON data
        if 'username' in data and 'password' in data:
            # Validate the login and password
            username = data['username']
            password = data['password']

            # Query user from the database
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE name = %s", (username,))
            user = cur.fetchone()
            cur.close()

            # Check if user exists and password is correct
            if user and check_password_hash(user[4], password):
                # Generate kubeToken and userToken
                kube_token = secrets.token_hex(16)
                user_token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

                # Return the tokens as a JSON response
                return jsonify({'kubeToken': kube_token, 'userToken': user_token})
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        else:
            return jsonify({'error': 'Username and password are required'}), 400
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

if __name__ == '__main__':
    # Run the application using gevent WSGI server
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

