from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from gevent.pywsgi import WSGIServer
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql-service'
app.config['MYSQL_USER'] = 'mysql'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'sample'

mysql = MySQL(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/data', methods=['POST'])
def add_data():
    cur = mysql.connection.cursor()
    name = request.json['name']
    age = request.json['age']
    cur.execute('''INSERT INTO user (name, age) VALUES (%s, %s)''', (name, age))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Data added successfully'})

if __name__ == '__main__':
    #app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
