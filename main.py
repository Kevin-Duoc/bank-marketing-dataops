import os
import sys
import logging

#inyeccion de la ruta de src al sistema para importar modulos locales
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

#importacion de las 4 fases del src
from ingesta import extraer_datos
from limpieza import limpiar_datos
from validacion import validar_datos
from carga import cargar_datos

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
        
        DATA_PATH = os.path.join(BASE_DIR, 'data', '02_bank.csv')
        
        #fase 1: ingesta
        print("[+] Ejecutando Fase 1: Ingesta de datos...")
        df_bruto = extraer_datos(DATA_PATH)
        
        #fase 2: limpieza
        print("[+] Ejecutando Fase 2: Limpieza defensiva...")
        df_limpio = limpiar_datos(df_bruto)
        
        #fase 3: validacion
        print("[+] Ejecutando Fase 3: Validacion estricta de esquema...")
        df_validado = validar_datos(df_limpio)
        
        # FASE 4: CARGA (Nueva fase integrada)
        print("[+] Ejecutando Fase 4: Carga masiva en AWS EC2 MySQL...")
        cargar_datos(df_validado)
        
        print("\n=== PIPELINE PROCESADO Y CARGADO CON EXITO ===")
        logging.info("Ejecucion del pipeline completo finalizada sin anomalias.")

    except Exception as e:
        print(f"\n[!] CRITICAL ERROR: El pipeline ha fallado. Verifica pipeline.log.")
        logging.error(f"Falla global en el orquestador main.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_pipeline()