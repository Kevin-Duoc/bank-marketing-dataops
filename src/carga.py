import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import logging

# 1. Configurar Logs (Requisito de la actividad) 
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_datos_mysql():
    connection = None
    try:
        # 2. Configuración de Conexión 
        # AJUSTA ESTOS DATOS SEGÚN TU INSTALACIÓN
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'localhost',
            'database': 'pipeline_vr'
        }

        logging.info("Iniciando fase de CARGA a MySQL...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 3. Crear Tabla según tipos de datos (DDL) 
            # Usaremos los campos del dataset de VR que ya validaste
            cursor.execute("DROP TABLE IF EXISTS usuarios_vr;")
            cursor.execute("""
                CREATE TABLE usuarios_vr (
                    UserID INT PRIMARY KEY,
                    Age INT,
                    Gender VARCHAR(50),
                    VRHeadset VARCHAR(100),
                    Duration FLOAT,
                    MotionSickness INT,
                    Riesgo_Mareo VARCHAR(50)
                );
            """)
            logging.info("Tabla 'usuarios_vr' creada o reiniciada con éxito.")

            # 4. Leer datos validados
            ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_validated.csv')
            df = pd.read_csv(ruta_csv)

            # --- LA SOLUCIÓN: FILTRAR Y ORDENAR COLUMNAS ---
            # Seleccionamos solo las 7 columnas exactas que la tabla de MySQL está esperando
            columnas_bd = ['UserID', 'Age', 'Gender', 'VRHeadset', 'Duration', 'MotionSickness', 'Riesgo_Mareo']
            df_filtrado = df[columnas_bd]

            # 5. Inserción Controlada (DML)
            sql_insert = """INSERT INTO usuarios_vr (UserID, Age, Gender, VRHeadset, Duration, MotionSickness, Riesgo_Mareo) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            # Convertimos el DataFrame ya filtrado a una lista de tuplas
            datos = [tuple(x) for x in df_filtrado.values]
            
            cursor.executemany(sql_insert, datos)
            connection.commit()
            
            mensaje = f"CARGA EXITOSA: Se insertaron {cursor.rowcount} registros en MySQL."
            print(mensaje)
            logging.info(mensaje)

    except Error as e:
        mensaje_error = f"Error crítico en la carga: {e}"
        print(mensaje_error)
        logging.error(mensaje_error)
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Conexión a MySQL cerrada.")

if __name__ == "__main__":
    cargar_datos_mysql()