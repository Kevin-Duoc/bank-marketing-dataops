import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

#cargar las variables del archivo .env
load_dotenv()

#1 configuración de la página
st.set_page_config(page_title="Dashboard Marketing DataOps", layout="wide")
st.title("Dashboard de Campañas de Marketing (AWS)")
st.markdown("Monitor avanzado de datos ingeridos desde el Pipeline DataOps hacia AWS EC2 MySQL.")

#2 credenciales de AWS leídos desde .env
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASS')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DB = os.getenv('DB_NAME')

#3 conexión y extraccion con cache
@st.cache_data
def cargar_datos_aws():
    string_conexion = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    engine = create_engine(string_conexion)
    df = pd.read_sql("SELECT * FROM clientes_marketing", engine)
    return df

# 4. Renderizado de la Interfaz
#4 renderizado de la inferfaz
try:
    df = cargar_datos_aws()
    st.success(f"Conexión exitosa a la nube. Registros validados: {len(df)}")
    
    #1 KPIs
    st.subheader("Indicadores Clave")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clientes", f"{len(df):,}")
    with col2:
        st.metric("Promedio de Edad", f"{int(df['age'].mean())} años")
    with col3:
        st.metric("Balance Promedio", f"${df['balance'].mean():.2f}")
    with col4:
        #calcula el porcentaje de personas que dijeron que "sí" al depósito
        tasa_exito = (len(df[df['deposit'] == 'yes']) / len(df)) * 100
        st.metric("Tasa de Éxito (Conversión)", f"{tasa_exito:.1f}%")
        
    st.divider() #línea separadora visual
    
    #2 gráficos visuales
    st.subheader("Análisis Visual Rápido")
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.markdown("**Distribución de Clientes por Profesión**")
        #cuenta cuántos hay por trabajo y dibuja un gráfico de barras
        st.bar_chart(df['job'].value_counts())
        
    with col_graf2:
        st.markdown("**Resultados de la Campaña (Depósito: Sí/No)**")
        #cuenta cuántos aceptaron o rechazaron y dibuja el gráfico
        st.bar_chart(df['deposit'].value_counts())

    st.divider()
        
    #3 tabla de datos
    st.subheader("Muestra de Datos (Head 1000)")
    st.dataframe(df.head(1000))

except Exception as e:
    st.error(f"Error conectando a AWS: {e}")