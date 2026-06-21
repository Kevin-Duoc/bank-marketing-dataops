import logging
import os

#configuracion del Logging nativo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'pipeline.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def limpiar_datos(df):
    """
    Fase de Limpieza: Aplica filtros defensivos sobre el DataFrame en memoria.
    """
    try:
        logging.info("Fase 2: Iniciando proceso de limpieza y transformacion...")

        #agregado: para guardar la cantidad inicial para calcular el KPI de perdida
        filas_originales = len(df)
        
        #1 detectar y eliminar duplicados
        duplicados_antes = df.duplicated().sum()
        if duplicados_antes > 0:
            df = df.drop_duplicates()
            logging.info(f"Limpieza: Se encontraron y eliminaron {duplicados_antes} registros duplicados.")
        else:
            logging.info("Limpieza: No se detectaron registros duplicados en el dataset.")

        #2 control defensivo de valores nulos (Missing Values)
        nulos_totales = df.isnull().sum().sum()
        if nulos_totales > 0:
            # En DataOps bancario, si faltan datos clave, a veces se imputan o se borran.
            # Aqui borraremos filas con nulos para asegurar la calidad estricta en AWS.
            df = df.dropna()
            logging.info(f"Limpieza: Se eliminaron filas con valores nulos. Total nulos detectados: {nulos_totales}")
        else:
            logging.info("Limpieza: Cero valores nulos detectados. Calidad de celdas estricta aprobada.")

        #registro del KPI de salida en el log
        filas, columnas = df.shape
        logging.info(f"Limpieza finalizada exitosamente. Volumen limpio en RAM: {filas} filas.")

        #3 Alera KPI critica
        filas_eliminadas = filas_originales - filas
        porcentaje_perdida = (filas_eliminadas / filas_originales) * 100 if filas_originales > 0 else 0

        if porcentaje_perdida >= 5.0:
            logging.critical(f"ALERTA KPI: Se eliminó el {porcentaje_perdida:.2f}% de los datos. Revisar calidad de origen.")
        else:
            logging.info(f"KPI Saludable: Integridad de datos al {100 - porcentaje_perdida:.2f}%.")
 
        return df

    except Exception as e:
        logging.error(f"Falla en Fase de Limpieza: {e}")
        raise e