# Utiliser une image de base Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source dans le conteneur
# COPY prod/ /app/

# Exposer le port sur lequel le serveur DNS écoute
EXPOSE 53

# Commande pour exécuter le serveur DNS
CMD ["python", "dns_random.py"]
