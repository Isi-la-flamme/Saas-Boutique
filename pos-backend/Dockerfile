FROM python:3.11-slim
WORKDIR /app
# Copie uniquement le fichier des dépendances pour mettre en cache la couche 'pip install'
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Utilisation de Gunicorn/Uvicorn pour la production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY . .
