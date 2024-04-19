# Utilisez une image de base Python
FROM python:3.9

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installez les dépendances Python spécifiées dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de votre application dans le conteneur
COPY . .

# Exposez le port sur lequel votre application Flask s'exécute
EXPOSE 5000

# Commande pour exécuter votre application Flask
CMD ["python", "app.py"]
