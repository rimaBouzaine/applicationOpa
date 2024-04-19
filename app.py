from flask import Flask, jsonify
import subprocess
from gevent.pywsgi import WSGIServer
app = Flask(__name__)
# Définition du label pour l'application Flask
app.config['LABEL_NAME'] = 'my-flask-app'
@app.route('/my-api')
def get_services():
    try:
        # Exécute la commande `kubectl get svc` en tant que sous-processus
        #result = subprocess.run(['kubectl', 'get', 'svc'], capture_output=True, text=True)
        result = subprocess.run(['kubectl', 'get', 'svc','-n','gatekeeper-system'], capture_output=True, text=True)
        # Vérifie le code de sortie de la commande
        if result.returncode == 0:
            print("Bonjour")
            # Si la commande a réussi, retourne la sortie en tant que réponse JSON
            return jsonify({'your-output': result.stdout})
        else:
            print("ERRORRRRR")
            # Si la commande a échoué, retourne un message d'erreur
            return jsonify({'your-custom-error': result.stderr}), 500
    except Exception as e:
        # En cas d'erreur, retourne un message d'erreur interne du serveur
        return jsonify({'error': str(e)}), 500
@app.route('/is-up')
def is_up():
    return 'Hello World'
if __name__ == '__main__':
   # app.run(host='0.0.0.0', port=5000)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
