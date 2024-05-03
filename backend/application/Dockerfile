# Utiliser une image Python officielle comme image de base
FROM python:3.9

# Install necessary dependencies
RUN apt-get update && apt-get install -y apt-transport-https gnupg
RUN apt install curl -y
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Installation des dépendances
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --no-cache-dir -r requirements.txt

# Copie de tous les fichiers du répertoire actuel dans le conteneur
COPY . .

# Commande à exécuter lors du démarrage du conteneur
CMD [ "python", "./app.py" ]

