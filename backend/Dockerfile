# Utiliser une image Python officielle comme image de base
FROM python:3.9

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installation des dépendances
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --no-cache-dir -r requirements.txt

# Copie de tous les fichiers du répertoire actuel dans le conteneur
COPY . .

# Commande à exécuter lors du démarrage du conteneur
CMD [ "python", "./app.py" ]

