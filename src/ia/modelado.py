import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# aeguramos que Python sepa buscar en esta misma carpeta (src/ia/)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoreo import medir_recursos
from evaluacion import evaluar_modelo

def descargar_datos_aws():
    """
    Se conecta a la tabla limpia en AWS y descarga los datos para la IA.
    """
    print("\n[+] 1. Conectando a AWS para descargar datos limpios...")
    load_dotenv()
    
    #se arma la llave con el .env
    USER = os.getenv('DB_USER')
    PASSWORD = os.getenv('DB_PASS')
    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')
    DB = os.getenv('DB_NAME')
    
    string_conexion = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    motor = create_engine(string_conexion)
    
    #descarga la tabla directamente a un DataFrame de Pandas
    query = "SELECT * FROM clientes_marketing"
    df = pd.read_sql(query, con=motor)
    
    print(f"  -> Descarga exitosa. Filas obtenidas: {len(df)}")
    return df

def preparar_datos(df):
    """
    Transforma el texto a números (Dummy Variables) y divide el curso en:
    80% para estudiar (Train) y 20% para el examen final (Test).
    """
    print("\n[+] 2. Preparando datos (Traduciendo palabras a matemáticas)...")
    
    #separa la variable que queremos predecir ('deposit')
    y = df['deposit'].map({'yes': 1, 'no': 0})
    X = df.drop('deposit', axis=1)
    
    #convierte todas las columnas de texto a binario (0 y 1)
    X_numerico = pd.get_dummies(X, drop_first=True)
    
    #reparte los datos
    X_train, X_test, y_train, y_test = train_test_split(X_numerico, y, test_size=0.2, random_state=42)
    
    print(f"  -> Datos de Entrenamiento: {X_train.shape[0]} filas")
    print(f"  -> Datos de Examen (Test): {X_test.shape[0]} filas")
    return X_train, X_test, y_train, y_test

# --- LOS MODELOS DE INTELIGENCIA ARTIFICIAL ---
@medir_recursos
def entrenar_regresion_logistica(X_train, y_train, X_test, y_test):
    print("\n[+] 3. Entrenando Modelo 1: Regresión Logística (Básico)...")
    modelo = LogisticRegression(max_iter=3000)
    modelo.fit(X_train, y_train)
    
    #el modelo rinde el examen
    predicciones = modelo.predict(X_test)
    
    #el juez evalúa las respuestas
    ##evaluar_modelo(y_test, predicciones, "Regresión Logística")
    return evaluar_modelo(y_test, predicciones, "Regresión Logística")

@medir_recursos
def entrenar_random_forest(X_train, y_train, X_test, y_test):
    print("\n[+] 4. Entrenando Modelo 2: Random Forest (Avanzado)...")
    #crea un bosque de 100 árboles de decisión
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    #el modelo rinde el examen
    predicciones = modelo.predict(X_test)
    
    #el juez evalúa las respuestas
    ##evaluar_modelo(y_test, predicciones, "Random Forest")
    return evaluar_modelo(y_test, predicciones, "Random Forest")

if __name__ == "__main__":
    print("=== INICIANDO LABORATORIO DE IA DATAOPS ===")
    
    #1 bajar datos
    df_aws = descargar_datos_aws()
    
    #2 preparar
    X_train, X_test, y_train, y_test = preparar_datos(df_aws)
    
    #3 probando modelos
    metricas_rl = entrenar_regresion_logistica(X_train, y_train, X_test, y_test)
    metricas_rf = entrenar_random_forest(X_train, y_train, X_test, y_test)

    #4 exportar JSON Dinámico
    import json
    resultados_dinamicos = {
        "Regresion Logistica": metricas_rl,
        "Random Forest": metricas_rf
    }
    
    ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'metricas_ia.json')
    with open(ruta_json, 'w') as f:
        json.dump(resultados_dinamicos, f, indent=4)
        
    print(f"\n[+] Métricas dinámicas exportadas a {ruta_json}")
    
    print("\n=== COMPARATIVA FINALIZADA ===")