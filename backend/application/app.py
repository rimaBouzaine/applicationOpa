import subprocess
from flask import Flask, Response, jsonify, request, make_response  # **Ajout de make_response**
from flask_mysqldb import MySQL
from gevent.pywsgi import WSGIServer
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # **Ajout de la configuration CORS plus complète**

# MySQL Configuration
app.config['MYSQL_HOST'] = 'mysql-service'
app.config['MYSQL_USER'] = 'mysql'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'sample'

mysql = MySQL(app)

@app.route('/isup')
def isup():
    return '200 OK'

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
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_preflight_response()  # **Ajout de la réponse preflight**
    elif request.method == "POST":
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
                    result = subprocess.run(['kubectl', 'create', 'token', 'my-svc-account'], capture_output=True, text=True)
                    if result.returncode == 0:
                        kube_token = result.stdout.strip()
                        user_token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, kube_token, algorithm='HS256')  # **Ajout de l'algorithme pour jwt.encode**
                        return jsonify({'kubeToken': kube_token, 'userToken': user_token})
                    else:
                        error_msg = result.stderr.strip() if result.stderr else 'Failed to generate kubeToken'
                        return jsonify({'message': error_msg}), 500
                else:
                    return jsonify({'message': 'Invalid credentials'}), 401
            else:
                return jsonify({'error': 'Username and password are required'}), 400
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

def _build_cors_preflight_response():
    response = make_response()  # **Ajout de make_response**
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

TARGET_API_BASE_URL = "https://kubernetes.default.svc"

@app.route('/proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    # Build the full URL for the target service API
    url = f"{TARGET_API_BASE_URL}/{path}"
    
    # Forward the request to the target service API
    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        files=request.files,
        verify=False,
    )
    
    response_headers = dict(response.headers)
    # Remove 'Transfer-Encoding' header if 'Content-Length' is present
    #if 'Content-Length' in response_headers:
    response_headers.pop('Transfer-Encoding', None)


    # Create a Flask Response object from the service API response
    proxy_response = Response(
        response.content,
        status=response.status_code,
        headers=response_headers,
    )
    print("I return a response........====>>>>")   
    return proxy_response

if __name__ == '__main__':
    # Run the application using gevent WSGI server
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
