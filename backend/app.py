from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from gevent.pywsgi import WSGIServer
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import secrets
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql-service'
app.config['MYSQL_USER'] = 'mysql'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'sample'
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Clé secrète aléatoire

mysql = MySQL(app)

# Fonction pour hasher le mot de passe
def hash_password(password):
    return generate_password_hash(password)
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/data', methods=['POST'])
def add_data():
    cur = mysql.connection.cursor()
    name = request.json['name']
    age = request.json['age']
    email = request.json['email']
    password = hash_password(request.json['password'])  # Hasher le mot de passe
    cur.execute('''INSERT INTO user (name, age, email, password) VALUES (%s, %s, %s, %s)''', (name, age, email, password))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Data added successfully'})

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return jsonify({'message': 'Authentification requise'}), 401


    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE name = %s", (username,))
    user = cur.fetchone()
    cur.close()
#   return jsonify({'user':check_password_hash(user[4],password)}),401 
    if user and check_password_hash(user[4], password):
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401
'''
    if user and check_password_hash(user[4], password):
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401
'''
if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
    app.debug = True
