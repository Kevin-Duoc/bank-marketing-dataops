import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors
import os
import logging

#1. configuracion logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def validar_con_pandera(ruta_entrada, ruta_validos, ruta_reporte_errores):
    try:
        logging.info("Iniciando validacion con PANDERA...")
        print("Escaneando datos con el esquema de Pandera...")
        
        #lee los datos limpios
        df = pd.read_csv(ruta_entrada)
        
        # --- DEFINICIÓN DEL CONTRATO DE DATOS (ESQUEMA) ---
        #se le dice a pandora como debe ser el archivo perfecto
        schema = pa.DataFrameSchema({
            #3 reglas estructurales
            "UserID": pa.Column(int, unique=True),               # 1. Clave primaria única
            "Duration": pa.Column(float, nullable=False),        # 2. No puede estar vacío (nulo)
            "Age": pa.Column(int, checks=[
                pa.Check.greater_than(0),                        # 3. La edad debe ser mayor a 0
                
                # REGLAS SEMÁNTICAS (Mínimo 2)
                pa.Check.in_range(10, 100)                       # 1. Rango lógico de edad (10 a 100 años)
            ]),
            "Riesgo_Mareo": pa.Column(str, checks=[
                pa.Check.isin(['Alto Riesgo', 'Bajo Riesgo'])    # 2. Solo se permiten estos dos textos exactos
            ])
        })

        # --- EJECUCIÓN DE LA VALIDACIÓN ---
        try:
            # lazy=True hace que revise TODO el archivo antes de detenerse
            df_validado = schema.validate(df, lazy=True)
            
            # Si pasa directo aquí, es que todo estaba 100% perfecto
            validos = df_validado
            errores = pd.DataFrame()
            
        except SchemaErrors as err:
            # Si Pandera encuentra errores, los atrapamos aquí
            # err.failure_cases es un reporte automático de Pandera con lo que falló
            errores = err.failure_cases
            
            # Separamos las filas buenas de las malas
            indices_malos = errores['index'].dropna().unique()
            validos = df[~df.index.isin(indices_malos)]

        # --- GUARDAR RESULTADOS ---
        # Guardar los datos buenos
        validos.to_csv(ruta_validos, index=False)
        
        # Guardar el reporte de errores
        os.makedirs(os.path.dirname(ruta_reporte_errores), exist_ok=True)
        if not errores.empty:
            errores.to_csv(ruta_reporte_errores, index=False)

        mensaje = f"Validacion terminada. Validos: {len(validos)} | Errores detectados: {len(errores)}"
        logging.info(mensaje)
        print(mensaje)
        if not errores.empty:
            print(f"Reporte de errores detallado en: {ruta_reporte_errores}")

    except Exception as e:
        logging.error(f"Error crítico en validación: {e}")
        print(f"Ocurrió un error crítico: {e}")

if __name__ == "__main__":
    archivo_entrada = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_clean.csv')
    archivo_validos = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'vr_validated.csv')
    reporte_errores = os.path.join(os.path.dirname(__file__), '..', 'data', 'reports', 'errores_pandera.csv')
    
    validar_con_pandera(archivo_entrada, archivo_validos, reporte_errores)