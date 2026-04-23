import pandas as pd
import numpy as np
import os
import logging

# 1. configurar los logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def limpiar_datos_vr(ruta_entrada, ruta_salida):
    try:
        logging.info("Iniciando la limpieza de datos de Realidad Virtual")
        print("Cargando y limpiando el dataset VR")
        
        #lee el csv
        df = pd.read_csv(ruta_entrada)
        
        #1. elimina columnas duplicadas
        df = df.drop_duplicates()
        
        #2. estandariza texto
        df['Gender'] = df['Gender'].str.strip().str.capitalize()
        df['VRHeadset'] = df['VRHeadset'].str.strip().str.title()
        
        #3. trata de nulos
        df['Age'] = df['Age'].fillna(df['Age'].median()).astype(int) # Edad con mediana
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
        
        #4. estandarizar números: redondea la duración a 2 decimales
        df['Duration'] = df['Duration'].round(2)
        
        #5. creación de columna derivada
        #clasifica el nivel de mareo (MotionSickness) en categorías
        #si es mayor o igual a 6, es "Alto Riesgo", de lo contrario "Bajo Riesgo"
        df['Riesgo_Mareo'] = np.where(df['MotionSickness'] >= 6, 'Alto Riesgo', 'Bajo Riesgo')
        
        #6. guarda el archivo limpio en processed
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        df.to_csv(ruta_salida, index=False)
        
        logging.info(f"Limpieza exitosa. Archivo guardado en {ruta_salida}")
        print(f"Datos limpios, transformados y guardados en {ruta_salida}!")

    except Exception as e:
        logging.error(f"Error en la limpieza: {e}")
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    #la ruta al archivo que descargamos con la ingesta
    archivo_sucio = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'data.csv')
    
    #la ruta donde guardaremos el archivo listo
    archivo_limpio = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_clean.csv')
    
    limpiar_datos_vr(archivo_sucio, archivo_limpio)