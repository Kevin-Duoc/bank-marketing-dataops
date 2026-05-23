import os
import shutil
import logging

# 1. Configurar los logs (el registro de actividad)
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ingerir_desde_local(ruta_origen, ruta_destino):
    try:
        logging.info(f"Iniciando ingesta desde ruta local: {ruta_origen}")
        print("Buscando el archivo CSV...")
        
        # 2. Verificar si el archivo realmente existe en la ruta origen
        if not os.path.exists(ruta_origen):
            raise FileNotFoundError(f"No se encontro el archivo en: {ruta_origen}")
        
        # 3. Crea la carpeta de destino (data/raw) si no existe
        os.makedirs(ruta_destino, exist_ok=True)
        
        # Definir la ruta completa de destino
        nombre_archivo = os.path.basename(ruta_origen)
        destino_completo = os.path.join(ruta_destino, nombre_archivo)
        
        # 4. Copiar el archivo a la carpeta de datos crudos
        shutil.copy(ruta_origen, destino_completo)
        
        logging.info(f"Ingesta exitosa. Archivo copiado a {destino_completo}")
        print(f"¡Archivo '{nombre_archivo}' copiado correctamente a {ruta_destino}!")

    except Exception as e:
        logging.error(f"Error en la ingesta local: {e}")
        print(f"Ocurrio un error: {e}")

if __name__ == "__main__":
    # --- CONFIGURACIÓN DE RUTAS ---
    
    # ⚠️ REEMPLAZA 'tu_archivo.csv' por el nombre real de tu archivo con su extensión .csv
    nombre_del_csv = "02_bank.csv" 
    
    # Tu ruta exacta combinada con el nombre del archivo
    ruta_csv_origen = os.path.join(r"C:\Users\ssvic\OneDrive\Escritorio\Evaluacion gestion-Ia\DataSets", nombre_del_csv)
    
    # La carpeta dentro de tu proyecto donde caerán los datos (../data/raw)
    carpeta_crudos = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    
    # Ejecutar la función
    ingerir_desde_local(ruta_csv_origen, carpeta_crudos)