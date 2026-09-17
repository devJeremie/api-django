# Image de dev — exécute manage.py runserver, pas un serveur WSGI/ASGI de
# production. La base slim garde l'image légère ; les paquets apt ci-dessous
# ne servent qu'à compiler mysqlclient (une extension C) lors du pip-install.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système nécessaires pour compiler mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt est copié et installé avant le reste des sources pour
# que le cache de layers de Docker soit réutilisé d'un build à l'autre tant
# que les dépendances n'ont pas changé (les modifications du code source
# seules n'invalident pas ce layer).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0, pas 127.0.0.1 — le serveur de dev doit accepter les connexions
# venant de l'extérieur du conteneur (c.-à-d. depuis l'hôte, via le mapping
# de port de docker-compose), pas seulement depuis localhost à l'intérieur du conteneur.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
