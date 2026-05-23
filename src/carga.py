import sys
import os
import logging
import time

# Configuración de logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import pandas as pd
    import mysql.connector
    from mysql.connector import Error
except ImportError as e:
    mensaje_error = f"ERROR CRÍTICO: Falta instalar una libreria. Ejecuta 'pip install pandas mysql-connector-python'. Detalle: {e}"
    print(mensaje_error)
    logging.error(mensaje_error)
    sys.exit(1)

def cargar_datos_mysql(host, user, password, database):
    connection = None
    start_time = time.time() # Para medir el KPI de Latencia (Time-to-Data)
    try:
        logging.info("Iniciando fase de CARGA a MySQL remoto en AWS...")
        print("Conectando con el servidor MySQL en AWS EC2...")
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Recrear tabla limpia del caso bancario
            print("Reiniciando la tabla 'bank_marketing' en la base de datos...")
            cursor.execute("DROP TABLE IF EXISTS bank_marketing;")
            cursor.execute("""
                CREATE TABLE bank_marketing (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    age INT,
                    job VARCHAR(100),
                    marital VARCHAR(50),
                    education VARCHAR(100),
                    balance FLOAT,
                    `default` VARCHAR(10),
                    housing VARCHAR(10),
                    loan VARCHAR(10),
                    contact VARCHAR(50),
                    day INT,
                    month VARCHAR(20),
                    duration FLOAT,
                    campaign INT,
                    pdays INT,
                    previous INT,
                    poutcome VARCHAR(50),
                    deposit VARCHAR(10),
                    perfil_cliente VARCHAR(50)
                );
            """)
            logging.info("Tabla 'bank_marketing' reiniciada con éxito en AWS.")

            # Leer datos validados del paso anterior
            ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'bank_validated.csv')
            if not os.path.exists(ruta_csv):
                raise FileNotFoundError(f"No se encontróo el archivo validado en: {ruta_csv}")
                
            df = pd.read_csv(ruta_csv)
            df = df.where(pd.notnull(df), None) # Reemplazar NaN por None para MySQL

            # Columnas exactas que se leerán del DataFrame
            columnas_bd = ['age', 'job', 'marital', 'education', 'balance', 'default', 'housing', 
                           'loan', 'contact', 'day', 'month', 'duration', 'campaign', 'pdays', 
                           'previous', 'poutcome', 'deposit', 'perfil_cliente']
            
            df_filtrado = df[columnas_bd]

            # Inserción masiva segura (DML)
            print("Inyectando registros en AWS EC2... ")
            placeholders = ", ".join(["%s"] * len(columnas_bd))
            columnas_str = ", ".join(['age', 'job', 'marital', 'education', 'balance', '`default`', 'housing', 
                                      'loan', 'contact', 'day', 'month', 'duration', 'campaign', 'pdays', 
                                      'previous', 'poutcome', 'deposit', 'perfil_cliente'])
            
            sql_insert = f"INSERT INTO bank_marketing ({columnas_str}) VALUES ({placeholders})"
            datos = [tuple(x) for x in df_filtrado.values]
            
            cursor.executemany(sql_insert, datos)
            connection.commit()
            
            mensaje = f"CARGA EXITOSA: Se insertaron {cursor.rowcount} registros en la EC2 de AWS."
            print(mensaje)
            logging.info(mensaje)
            
            # Registrar KPI: Latencia (Time-to-Data prometido en la sección 4.2 del informe)
            latencia_total = time.time() - start_time
            logging.info(f"KPI - Latencia de Ejecucion de Carga (Time-to-Data): {latencia_total:.2f} segundos.")

    except Error as e:
        # --- AQUÍ INTERCEPTAMOS EL ERROR DE CONEXIÓN (Código 2003) ---
        if e.errno == 2003:
            mensaje_error = f"Error al conectarse con la instancia EC2. El error tecnico es: {e}"
        else:
            mensaje_error = f"Error critico en la carga a AWS: {e}"
            
        print(mensaje_error)
        logging.error(mensaje_error)
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("Conexion a AWS cerrada de forma segura.")
            print("Conexion a la nube cerrada de forma segura.")

if __name__ == "__main__":
    # Dirección IP pública de tu instancia AWS EC2
    IP_EC2 = "44.204.208.68"
    
    # Ejecutar el proceso de carga hacia la base de datos remota
    cargar_datos_mysql(
        host=IP_EC2,
        user="root",
        password="root",
        database="pipeline_vr"
    )