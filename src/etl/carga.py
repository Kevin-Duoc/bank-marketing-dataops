from sqlalchemy import create_engine
import logging
import os
from dotenv import load_dotenv  #carga la librería para leer el archivo .env

#configuración de rutas para los Logs
##ya no es necesario debido a la ruta /src/etc
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# LOG_DIR = os.path.join(BASE_DIR, 'logs')
# os.makedirs(LOG_DIR, exist_ok=True)
# LOG_FILE = os.path.join(LOG_DIR, 'pipeline.log')

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

#cargar las variables de entorno del archivo .env automáticamente
load_dotenv()

def cargar_datos(df):
    """
    Fase de Carga: Inyecta el DataFrame validado en la base de datos MySQL en AWS EC2.
    """
    try:
        logging.info("Fase 4: Iniciando conexion TCP hacia AWS MySQL...")
        
        #leer las credenciales desde el archivo oculto .env
        USER = os.getenv('DB_USER')
        PASSWORD = os.getenv('DB_PASS')
        HOST = os.getenv('DB_HOST')
        PORT = os.getenv('DB_PORT')
        DB = os.getenv('DB_NAME')
        
        #construccion del Connection String para SQLAlchemy
        string_conexion = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
        engine = create_engine(string_conexion)
        
        logging.info(f"Conectando a base de datos '{DB}' en servidor remoto de AWS...")
        
        #carga masiva de datos mediante Pandas a SQL
        #actualizacion: cambie if_exists='replace' a if_exists='append' ya que al subir por lotes a la base de datos, el segundo lote sobreescribiria el primero
        df.to_sql(name='clientes_marketing', con=engine, if_exists='append', index=False)
        
        filas_cargadas = len(df)
        logging.info(f"Carga exitosa. {filas_cargadas} registros inyectados en la tabla 'clientes_marketing'.")
        logging.info("--- PIPELINE DATAOPS FINALIZADO CON EXITO ---")

    except Exception as e:
        logging.error(f"Falla Critica en conexion o inyeccion hacia AWS: {e}")
        raise e