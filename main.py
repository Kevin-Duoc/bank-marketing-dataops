import os
import sys
import logging

# Inyeccion de la ruta de src al sistema para poder importar los modulos locales
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importacion de las funciones de tus scripts del src
from ingesta import extraer_datos
from limpieza import limpiar_datos
from validacion import validar_datos

# Configuracion del Logging nativo en el archivo central
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'pipeline.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ejecutar_pipeline():
    try:
        print("\n=== INICIANDO PRUEBA DE INTEGRACION DATAOPS ===")
        logging.info("=== CONFIGURACION DE PRUEBA INCREMENTAL ===")
        
        # 1. Definicion de la ruta fisica del CSV en la carpeta data/
        DATA_PATH = os.path.join(BASE_DIR, 'data', '02_bank.csv')
        
        # FASE 1: INGESTA (Extraccion)
        print("[+] Ejecutando Fase 1: Ingesta de datos...")
        df_bruto = extraer_datos(DATA_PATH)
        
        # FASE 2: LIMPIEZA (Transformacion)
        print("[+] Ejecutando Fase 2: Limpieza defensiva...")
        df_limpio = limpiar_datos(df_bruto)
        
        # FASE 3: VALIDACION (Contrato de Datos con Pandera)
        print("[+] Ejecutando Fase 3: Validacion estricta de esquema...")
        df_validado = validar_datos(df_limpio)
        
        # Fin de la prueba en memoria RAM
        print("\n=== PRUEBA FINALIZADA CON EXITO ===")
        print(f"Resultado en memoria RAM: {len(df_validado)} filas validadas y listas para AWS.")
        logging.info(f"Integracion local exitosa. Dataset listo para carga. Filas: {len(df_validado)}")

    except Exception as e:
        print(f"\n[!] EL PIPELINE HA FALLADO: Revisa pipeline.log para ver los detalles del error.")
        logging.error(f"Falla en la ejecucion del pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ejecutar_pipeline()