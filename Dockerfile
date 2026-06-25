FROM python:3.12-slim

WORKDIR /app

#instalar dependencias primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copia arquitectura (ETL, IA, Dashboard)
COPY . .

#Expone el puerto para el dashboard
EXPOSE 8501

#levanta streamlit como proceso principal
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]