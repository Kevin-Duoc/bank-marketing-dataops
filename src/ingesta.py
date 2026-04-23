import os
import logging

# 1. autenticación directa (inyectar Token de Kaggle)
os.environ['KAGGLE_API_TOKEN'] = "KGAT_28055ab7c96d802b7c1274a88abc2a48"
from kaggle.api.kaggle_api_extended import KaggleApi

# 2. configurar los logs (el registro de actividad)
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ingerir_desde_kaggle(dataset_id, ruta_destino):
    try:
        logging.info(f"Conectando a Kaggle para descargar: {dataset_id}")
        print("Autenticando con Kaggle y descargando datos...")
        
        # 3. inicia la API
        api = KaggleApi()
        api.authenticate()
        
        # 4. crea la carpeta raw si no existe
        os.makedirs(ruta_destino, exist_ok=True)
        
        # 5. descarga y descomprime directamente
        api.dataset_download_files(dataset_id, path=ruta_destino, unzip=True)
        
        logging.info(f"Ingesta exitosa. Archivos guardados en {ruta_destino}")
        print(f"Dataset descargado y descomprimido correctamente en {ruta_destino}!")

    except Exception as e:
        logging.error(f"Error en la conexión a Kaggle: {e}")
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    #id del dataset
    dataset_kaggle = "aakashjoshi123/virtual-reality-experiences"
    
    #la carpeta donde caeran los datos
    carpeta_crudos = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    
    ingerir_desde_kaggle(dataset_kaggle, carpeta_crudos)