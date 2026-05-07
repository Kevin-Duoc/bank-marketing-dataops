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
    import pandera.pandas as pa
    from pandera.errors import SchemaErrors
except ImportError as e:
    mensaje_error = f"ERROR CRITICO: Falta instalar una libreria. Ejecuta 'pip install pandas pandera'. Detalle: {e}"
    print(mensaje_error)
    logging.error(mensaje_error)
    sys.exit(1)  # Detiene la ejecución del script

def validar_con_pandera(ruta_entrada, ruta_validos, ruta_reporte_errores):
    try:
        logging.info("Iniciando validacion con PANDERA...")
        print("Escaneando datos con el esquema de Pandera...")
        
        #lee los datos limpios
        df = pd.read_csv(ruta_entrada)
        
        #ESQUEMA CONTRATO DE DATOS
        #se le dice a Pandora como debe ser el archivo perfecto
        schema = pa.DataFrameSchema({
            "UserID": pa.Column(int, unique=True),   
            "Duration": pa.Column(float, nullable=False),
            "Age": pa.Column(int, checks=[
                pa.Check.greater_than(0),     
                pa.Check.in_range(10, 100)   
            ]),
            "Riesgo_Mareo": pa.Column(str, checks=[
                pa.Check.isin(['Alto Riesgo', 'Bajo Riesgo'])
            ])
        })

        ##EJECUCION DE LA VALIDACION
        try:
            #lazy=True hace que revise TODO el archivo antes de detenerse
            df_validado = schema.validate(df, lazy=True)
            
            validos = df_validado
            errores = pd.DataFrame()
            
        except SchemaErrors as err:
            #si Pandera encuentra errores, quedan atrapados aqui 
            errores = err.failure_cases
            
            #separación de filas buenas y malas
            indices_malos = errores['index'].dropna().unique()
            validos = df[~df.index.isin(indices_malos)]

        #guarda los datos buenos
        validos.to_csv(ruta_validos, index=False)
        
        #guarda el reporte de errores
        os.makedirs(os.path.dirname(ruta_reporte_errores), exist_ok=True)
        if not errores.empty:
            errores.to_csv(ruta_reporte_errores, index=False)

        mensaje = f"Validacion terminada. Validos: {len(validos)} | Errores detectados: {len(errores)}"
        logging.info(mensaje)
        print(mensaje)
        if not errores.empty:
            print(f"Reporte de errores detallado en: {ruta_reporte_errores}")

    except Exception as e:
        logging.error(f"Error critico en validacion: {e}")
        print(f"Ocurrio un error critico: {e}")

if __name__ == "__main__":
    archivo_entrada = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_clean.csv')
    archivo_validos = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_validated.csv')
    reporte_errores = os.path.join(os.path.dirname(__file__), '..', 'data', 'reports', 'errores_pandera.csv')
    
    validar_con_pandera(archivo_entrada, archivo_validos, reporte_errores)