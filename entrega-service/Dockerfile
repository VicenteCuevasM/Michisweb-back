FROM python:3.11-slim

WORKDIR /app

# Copiamos y instalamos dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto interno de Uvicorn
EXPOSE 8000

# Ejecutamos Uvicorn apuntando a main:app en el puerto 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
