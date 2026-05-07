import sys
import os
import logging

#configuracion de logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

#control de dependencias
try:
    import pandas as pd
    import mysql.connector
    from mysql.connector import Error
except ImportError as e:
    mensaje_error = f"ERROR CRITICO: Falta instalar una libreria. Ejecuta 'pip install pandas mysql-connector-python'. Detalle: {e}"
    print(mensaje_error)
    logging.error(mensaje_error)
    sys.exit(1) #detiene script

def cargar_datos_mysql():
    connection = None
    try:
        #configuracion de conexion
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
            
            #creación de tablas según tipos de datos (DDL) 
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
            logging.info("Tabla 'usuarios_vr' creada o reiniciada con exito.")

            #lectura de datos validados
            ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_validated.csv')
            df = pd.read_csv(ruta_csv)

            #filtrar y ordenar las 7 columnas exactas que la tabla de MySQL está esperando
            columnas_bd = ['UserID', 'Age', 'Gender', 'VRHeadset', 'Duration', 'MotionSickness', 'Riesgo_Mareo']
            df_filtrado = df[columnas_bd]

            # 6. Inserción Controlada (DML)
            sql_insert = """INSERT INTO usuarios_vr (UserID, Age, Gender, VRHeadset, Duration, MotionSickness, Riesgo_Mareo) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            #convertir el DataFrame ya filtrado a una lista de tuplas
            datos = [tuple(x) for x in df_filtrado.values]
            
            cursor.executemany(sql_insert, datos)
            connection.commit()
            
            mensaje = f"CARGA EXITOSA: Se insertaron {cursor.rowcount} registros en MySQL."
            print(mensaje)
            logging.info(mensaje)

    except Error as e:
        mensaje_error = f"Error critico en la carga: {e}"
        print(mensaje_error)
        logging.error(mensaje_error)
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Conexion a MySQL cerrada.")

if __name__ == "__main__":
    cargar_datos_mysql()