import os
import sys
import logging
from sqlalchemy import create_engine, text #text para ejecutar comando SQL
from dotenv import load_dotenv #para conectar y vaciar la tabla


#inyeccion de la ruta de src al sistema para importar modulos locales
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

#importacion de las 4 fases del src
from etl.ingesta import extraer_datos
from etl.limpieza import limpiar_datos
from etl.validacion import validar_datos
from etl.carga import cargar_datos

#configuracion del logging nativo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'pipeline.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ejecutar_pipeline():
    try:
        print("\n=== INICIANDO PIPELINE DATAOPS (PRODUCCION) ===")
        logging.info("=== INICIANDO EJECUCION INTEGRAL DEL PIPELINE ---")
        
        #fase 0: vaciar la BD y evitar datos duplicados con el append
        print("[+] Limpiando base de datos remota para nueva ingesta...")
        load_dotenv()
        string_conexion = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        motor = create_engine(string_conexion)
        with motor.connect() as conexion:
            conexion.execute(text("TRUNCATE TABLE clientes_marketing"))
            conexion.commit()

        DATA_PATH = os.path.join(BASE_DIR, 'data', '02_bank.csv')
        
        #fase 1: ingesta (devuelve un iterador)
        print("[+] Ejecutando Fase 1: Ingesta de datos...")
        #actualizado 
        ## df_bruto = extraer_datos(DATA_PATH)
        iterador_lotes = extraer_datos(DATA_PATH, chunk_size=10000)
        
        #actualizado: bucle for para procesar lote por lote sin reventar la ram
        contador_lotes = 1
        for df_bruto in iterador_lotes:
            print(f"\n--- Procesando Lote {contador_lotes} ({len(df_bruto)} filas ---")
            #fase 2: limpieza
            print("[+] Ejecutando Fase 2: Limpieza defensiva...")
            df_limpio = limpiar_datos(df_bruto)
            
            #fase 3: validacion
            print("[+] Ejecutando Fase 3: Validacion estricta de esquema...")
            df_validado = validar_datos(df_limpio)
            
            # FASE 4: CARGA (Nueva fase integrada)
            print("[+] Ejecutando Fase 4: Carga masiva en AWS EC2 MySQL...")
            cargar_datos(df_validado)

            contador_lotes += 1
        
        print("\n=== PIPELINE PROCESADO Y CARGADO CON EXITO ===")
        logging.info("Ejecucion del pipeline completo finalizada sin anomalias.")

    except Exception as e:
        print(f"\n[!] CRITICAL ERROR: El pipeline ha fallado. Verifica pipeline.log.")
        logging.error(f"Falla global en el orquestador main.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_pipeline()