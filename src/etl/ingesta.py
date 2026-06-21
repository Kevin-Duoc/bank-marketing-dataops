import pandas as pd
import logging
import sys
import os

#Configuración de logging nativo
#crea el archivo pipeline.log automáticamente en la raíz
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

def extraer_datos(ruta_archivo, chunk_size=10000): #por lotes
    try:
        logging.info("--- INICIANDO PIPELINE DATAOPS ---")
        logging.info("Fase 1: Iniciando extraccion de datos (Pandas)...")
        
        #validación defensiva
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Error Crítico: No se encontró el CSV en {ruta_archivo}")

        #ingesta del Bank Marketing Dataset
        ## df = pd.read_csv(ruta_archivo, sep=',')
        #reemplazo: ahora lee el archivo en pedazos para no saturar ram
        df_iterador = pd.read_csv(ruta_archivo, sep=",", chunksize=chunk_size)

        #registro de la cantidad de datos en el log
        ## filas, columnas = df.shape
        ## logging.info(f"Ingesta exitosa. Volumen ingerido: {filas} filas y {columnas} columnas.")
        logging.info(f"Ingesta configurada exitosamente por lotes de {chunk_size} registros.")
        return df_iterador

    except Exception as e:
        logging.error(f"Falla en Ingesta: {e}")
        print(f"Error critico, revisa pipeline.log: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Como el archivo ahora está en src/etl/, subimos 3 niveles para llegar a la raíz.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #apunta a la carpeta data/02_bank.csv
    DATA_PATH = os.path.join(BASE_DIR, 'data', '02_bank.csv')
    
    #ejecuta la extracción
    ## df_bruto = extraer_datos(DATA_PATH)
    ## print(f"\nIngesta finalizada correctamente. Filas leídas en memoria: {len(df_bruto)}")
    #reemplazo: al ser iterador, no se puede usar len()
    iterador = extraer_datos(DATA_PATH)
    print("\nIngesta finalizada correctamente. Iterador listo en memoria.")