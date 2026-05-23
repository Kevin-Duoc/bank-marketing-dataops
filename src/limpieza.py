import os
import pandas as pd
import numpy as np
import logging

# Configurar los logs
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'pipeline.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def limpiar_datos_bancarios(ruta_entrada, ruta_salida):
    try:
        logging.info("Iniciando la limpieza de datos bancarios (02_bank)")
        print("Cargando y limpiando el dataset bancario...")
        
        if not os.path.exists(ruta_entrada):
            raise FileNotFoundError(f"No se encontro el archivo crudo en: {ruta_entrada}")
            
        df = pd.read_csv(ruta_entrada)
        
        # Guardar volumen inicial para KPI de completitud
        total_registros_inicial = len(df)
        
        # 1. Elimina filas duplicadas
        df = df.drop_duplicates()
        total_registros_post_duplicados = len(df)
        logging.info(f"Se eliminaron {total_registros_inicial - total_registros_post_duplicados} filas duplicadas.")
        
        # 2. Estandarizar texto
        columnas_texto = ['job', 'marital', 'education', 'default', 'housing', 'loan', 'contact', 'month', 'poutcome', 'deposit']
        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
        
        # 3. Tratamiento de nulos en variables numéricas importantes
        if 'age' in df.columns:
            df['age'] = df['age'].fillna(df['age'].median()).astype(int)
            
        if 'balance' in df.columns:
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce')
            df['balance'] = df['balance'].fillna(0).round(2)
            
        if 'duration' in df.columns:
            df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
            df['duration'] = df['duration'].fillna(df['duration'].median()).round(2)
            
        # 4. Creación de columna derivada (Regla de negocio)
        if 'balance' in df.columns:
            condiciones = [
                (df['balance'] < 0),
                (df['balance'] >= 0) & (df['balance'] <= 5000),
                (df['balance'] > 5000)
            ]
            categorias = ['Deudor', 'Regular', 'Premium']
            df['perfil_cliente'] = np.select(condiciones, categorias, default='No Identificado')
        
        # 5. Guardar archivo limpio
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        df.to_csv(ruta_salida, index=False)
        
        # Registro de KPI en el LOG
        tasa_preservacion = (len(df) / total_registros_inicial) * 100
        logging.info(f"KPI - Tasa de Completitud y Preservacion de Datos: {tasa_preservacion:.2f}% (Registros finales: {len(df)} de {total_registros_inicial})")
        
        logging.info(f"Limpieza exitosa. Archivo procesado guardado en {ruta_salida}")
        print(f"¡Datos limpios, transformados y guardados en {ruta_salida}!")

    except Exception as e:
        logging.error(f"Error en la fase de limpieza: {e}")
        print(f"Ocurrió un error en la limpieza: {e}")

if __name__ == "__main__":
    archivo_sucio = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', '02_bank.csv')
    archivo_limpio = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'bank_clean.csv')
    limpiar_datos_bancarios(archivo_sucio, archivo_limpio)