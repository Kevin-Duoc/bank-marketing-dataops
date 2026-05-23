import sys
import os
import logging

# Configuración de logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import pandas as pd
    import pandera as pa
    from pandera.errors import SchemaErrors
except ImportError as e:
    mensaje_error = f"ERROR CRÍTICO: Falta instalar una librería. Ejecuta pip install. Detalle: {e}"
    print(mensaje_error)
    logging.error(mensaje_error)
    sys.exit(1)

def validar_con_pandera(ruta_entrada, ruta_validos, ruta_reporte_errores):
    try:
        logging.info("Iniciando validacion con PANDERA en datos bancarios...")
        print("Escaneando datos con el esquema de Pandera...")
        
        if not os.path.exists(ruta_entrada):
            raise FileNotFoundError(f"No se encontró el archivo limpio en: {ruta_entrada}")
            
        df = pd.read_csv(ruta_entrada)
        total_registros = len(df)
        
        # --- ESQUEMA CONTRATO DE DATOS (02_bank) ---
        schema_dict = {}
        
        if 'age' in df.columns:
            schema_dict['age'] = pa.Column(int, checks=[
                pa.Check.greater_than_or_equal_to(18), 
                pa.Check.less_than_or_equal_to(120)    
            ])
            
        if 'balance' in df.columns:
            schema_dict['balance'] = pa.Column(float, nullable=False)
            
        if 'duration' in df.columns:
            schema_dict['duration'] = pa.Column(float, checks=[
                pa.Check.greater_than_or_equal_to(0)   
            ])
            
        if 'perfil_cliente' in df.columns:
            schema_dict['perfil_cliente'] = pa.Column(str, checks=[
                pa.Check.isin(['Deudor', 'Regular', 'Premium', 'No Identificado'])
            ])

        schema = pa.DataFrameSchema(schema_dict, strict=False)

        ## EJECUCIÓN DE LA VALIDACIÓN
        try:
            df_validado = schema.validate(df, lazy=True)
            validos = df_validado
            errores = pd.DataFrame()
            error_rate = 0.0
            
        except SchemaErrors as err:
            errores = err.failure_cases
            indices_malos = errores['index'].dropna().unique()
            validos = df[~df.index.isin(indices_malos)]
            
            # Calcular KPI: Tasa de Fallas (Prometido en sección 4.2 del informe)
            error_rate = (len(indices_malos) / total_registros) * 100

        # Guardar datos aptos
        os.makedirs(os.path.dirname(ruta_validos), exist_ok=True)
        validos.to_csv(ruta_validos, index=False)
        
        # Guardar reporte de fallas si existen
        os.makedirs(os.path.dirname(ruta_reporte_errores), exist_ok=True)
        if not errores.empty:
            errores.to_csv(ruta_reporte_errores, index=False)

        # Registro del KPI en el archivo LOG
        logging.info(f"KPI - Tasa de Fallas en Contratos de Datos: {error_rate:.2f}%")
        
        mensaje = f"Validacion terminada. Validos: {len(validos)} | Filas con errores: {len(df) - len(validos)}"
        logging.info(mensaje)
        print(mensaje)
        
    except Exception as e:
        logging.error(f"Error critico en validacion: {e}")
        print(f"Ocurrio un error critico: {e}")

if __name__ == "__main__":
    archivo_entrada = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'bank_clean.csv')
    archivo_validos = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'bank_validated.csv')
    reporte_errores = os.path.join(os.path.dirname(__file__), '..', 'data', 'reports', 'errores_pandera.csv')
    validar_con_pandera(archivo_entrada, archivo_validos, reporte_errores)